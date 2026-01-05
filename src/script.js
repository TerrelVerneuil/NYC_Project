import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import gsap from 'gsap'

/**
 * Setup & Constants
 */
const NYC_CENTER = { lat: 40.7128, lon: -74.0060 }
const DATA_PATH = '/nyc_zipcodes_with_crime.geojson'

// Select UI Elements
const infoPanel = document.getElementById('infoPanel')
const poNameElem = document.getElementById('poName')
const zipCodeElem = document.getElementById('zipCode')
const boroughElem = document.getElementById('borough')
const crimeCountElem = document.getElementById('crimeCount')
const safetyScoreElem = document.getElementById('safetyScore')
const safetyLabel = document.getElementById('safetyLabel')
const crimeTypesElem = document.getElementById('crimeTypes')
const loading = document.getElementById('loading')
const zipSearch = document.getElementById('zipSearch')
const precinctNumElem = document.getElementById('precinctNum') // Add this at top

/**
 * Coordinate Projection
 */
function latLonToMeters(lat, lon) {
    const R = 6371000 
    const x = (lon - NYC_CENTER.lon) * (R * Math.cos(NYC_CENTER.lat * Math.PI / 180))
    const y = (lat - NYC_CENTER.lat) * R
    return { x: x / 500, y: y / 500 }
}

const canvas = document.querySelector('canvas.webgl')
const scene = new THREE.Scene()
scene.background = new THREE.Color(0x05050f)

const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
scene.add(ambientLight)

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
directionalLight.position.set(100, 200, 100)
scene.add(directionalLight)

const sizes = { width: window.innerWidth, height: window.innerHeight }
const camera = new THREE.PerspectiveCamera(45, sizes.width / sizes.height, 0.1, 5000)
camera.position.set(0, 500, 1400)

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
renderer.setSize(sizes.width, sizes.height)
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

const controls = new OrbitControls(camera, canvas)
controls.enableDamping = true

/**
 * Logic & Data
 */
let zipCodeMeshes = []
let hoveredObject = null

function getColorFromSafetyScore(score) {
    const hue = score * 0.30 
    return new THREE.Color().setHSL(hue, 0.9, 0.5)
}

function createZipGeometry(coordinates, height = 0.5) {
    const shapes = []
    const polygons = Array.isArray(coordinates[0][0][0]) ? coordinates : [coordinates]
    
    polygons.forEach(polygon => {
        const shape = new THREE.Shape()
        polygon[0].forEach((coord, i) => {
            const p = latLonToMeters(coord[1], coord[0])
            if (i === 0) shape.moveTo(p.x, p.y)
            else shape.lineTo(p.x, p.y)
        })
        shapes.push(shape)
    })

    const geometry = new THREE.ExtrudeGeometry(shapes, { depth: height, bevelEnabled: false })
    geometry.rotateX(-Math.PI / 2)
    return geometry
}

async function loadData() {
    try {
        const response = await fetch(DATA_PATH)
        const geoData = await response.json()

        geoData.features.forEach(feature => {
    const p = feature.properties
    
    // Normalize properties
    const zip = p.postalCode || p.zipcode || p.ZIPCODE || "N/A"
    const neighborhood = p.neighborhood || p.PO_NAME || "NYC Neighborhood"
    const borough = p.borough || p.COUNTY || "New York"
    const weight = p.weightedCrimeVal || 1
    const score = p.safetyScore !== undefined ? p.safetyScore : 0.5
    const precinct = p.precinct || "N/A" // <--- ADD THIS LINE

    const height = Math.max(weight / 8, 0.5)
    const geometry = createZipGeometry(feature.geometry.coordinates, height)
    
    const material = new THREE.MeshStandardMaterial({
        color: getColorFromSafetyScore(score),
        transparent: true,
        opacity: 0.8
    })

    const mesh = new THREE.Mesh(geometry, material)
    
    mesh.userData = { 
        ...p, 
        zip, 
        neighborhood, 
        borough, 
        score, 
        weight, 
        precinct, 
        baseHeight: height 
    }
    
    zipCodeMeshes.push(mesh)
    scene.add(mesh)
        })

        loading.style.opacity = '0'
        setTimeout(() => loading.style.display = 'none', 500)
    } catch (e) {
        console.error("Load Error", e)
    }
}


const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2()

window.addEventListener('mousemove', (e) => {
    mouse.x = (e.clientX / sizes.width) * 2 - 1
    mouse.y = -(e.clientY / sizes.height) * 2 + 1
})


function updateInfoPanel(data) {
    if (!data) return;

    // 1. Text Info
    poNameElem.textContent = data.neighborhood || data.PO_NAME || "Unknown Area";
    zipCodeElem.textContent = data.postalCode || data.zip || "---";
    boroughElem.textContent = data.borough || "---";
    crimeCountElem.textContent = data.crimeCount || "0";
    
    // 2. Precinct Info - Pull from the userData we just added
    if (precinctNumElem) {
        precinctNumElem.textContent = data.precinct !== "N/A" 
            ? `Precinct ${data.precinct}` 
            : "No Precinct Data";
    }
    
    // 3. Safety Score & Label
    const sScore = data.safetyScore !== undefined ? data.safetyScore : 0.5;
    safetyScoreElem.textContent = `${(sScore * 100).toFixed(0)}%`;
    
    if (sScore > 0.7) {
        safetyLabel.textContent = "SECURE";
        safetyLabel.style.color = "#7FFF00";
    } else if (sScore > 0.4) {
        safetyLabel.textContent = "MODERATE";
        safetyLabel.style.color = "#FFFF00";
    } else {
        safetyLabel.textContent = "HIGH RISK";
        safetyLabel.style.color = "#FF4500";
    }

    // 4. Crime Breakdown
    if (data.crimeBreakdown) {
        const breakdown = typeof data.crimeBreakdown === 'string' 
            ? JSON.parse(data.crimeBreakdown) 
            : data.crimeBreakdown;
        
        crimeTypesElem.innerHTML = Object.entries(breakdown)
            .map(([k, v]) => `
                <div style="display:flex; justify-content:space-between; width: 100%; margin-bottom: 4px;">
                    <span style="text-transform: capitalize; opacity: 0.8;">${k.toLowerCase()}</span>
                    <strong style="color: white;">${v}</strong>
                </div>`)
            .join('');
    }

    infoPanel.style.opacity = 1;
}
/**
 * Updated Search Logic
 */
zipSearch.addEventListener('input', (e) => {
    const val = e.target.value.trim();
    //digit zip limit
    if (val.length === 5) {
        const targetMesh = zipCodeMeshes.find(m => m.userData.zip === val);
        
        if (targetMesh) {
            // 1. Highlight the mesh
            zipCodeMeshes.forEach(m => m.material.emissive.set(0x000000));
            targetMesh.material.emissive.set(0x00ffff); 
            
           //update info panel when a user searches
            updateInfoPanel(targetMesh.userData);
            
            // look at zip code
            const center = new THREE.Vector3();
            targetMesh.geometry.computeBoundingBox();
            targetMesh.geometry.boundingBox.getCenter(center);
            
            gsap.to(controls.target, { x: center.x, y: 0, z: center.z, duration: 1.2, ease: "power2.inOut" });
        }
    }
});

/**
 * Updated Raycaster (Hover) Logic
 */
function updateRaycaster() {
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(zipCodeMeshes);

    if (intersects.length > 0) {
        const obj = intersects[0].object;
        if (hoveredObject !== obj) {
            if (hoveredObject) hoveredObject.material.emissive.set(0x000000);
            hoveredObject = obj;
            hoveredObject.material.emissive.set(0x333333);
            updateInfoPanel(hoveredObject.userData);
        }
    } else if (hoveredObject) {
        hoveredObject.material.emissive.set(0x000000);
        hoveredObject = null;
        infoPanel.style.opacity = 0;
    }
}

/**
 * Render Loop
 */
const tick = () => {
    controls.update()
    updateRaycaster()
    renderer.render(scene, camera)
    window.requestAnimationFrame(tick)
}

loadData()
tick()

window.addEventListener('resize', () => {
    sizes.width = window.innerWidth
    sizes.height = window.innerHeight
    camera.aspect = sizes.width / sizes.height
    camera.updateProjectionMatrix()
    renderer.setSize(sizes.width, sizes.height)
})