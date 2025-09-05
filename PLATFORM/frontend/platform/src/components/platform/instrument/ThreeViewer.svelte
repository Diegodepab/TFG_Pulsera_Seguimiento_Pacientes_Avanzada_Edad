<script>
  import BaseButton from "$components/argon_template/BaseButton.svelte";
  import { onDestroy } from "svelte";
  import { t } from "svelte-i18n";
  import { fade } from "svelte/transition";
  import * as THREE from "three";
  import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
  import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

  /**
   * @typedef {Object} ThreeViewerProps
   * @property {any} url
   * @property {boolean} [hideNotAvailableLabel]
   * @property {"lg"| "md"| "sm"} [iconSize]
   */

  /** @type ThreeViewerProps */
  let {
    url,
    hideNotAvailableLabel = false,
    iconSize = "lg",
  } = $props();

  /** @type boolean */
  let showCentralLoadingSpinner = $state(false);

  /** @type HTMLDivElement */
  let container = $state();

  /** @type ResizeObserver */
  let resizeContainerModelObserver;

  /** @type boolean */
  let isFullScreen = false;

  let scene;
  let camera;
  let renderer;

  /** @type boolean - indicate if model is available */
  let available = $state(true);

  onDestroy(() => {
    resizeContainerModelObserver?.disconnect();
    renderer?.dispose();
  });

  /**
   * Initializes a new THREE.js scene with a camera, renderer, lights, and loads a 3D model.
   * Sets up orbit controls for camera manipulation and handles window resizing.
   *
   * @requires THREE - Three.js library
   * @requires OrbitControls - Three.js OrbitControls module
   * @requires GLTFLoader - Three.js GLTFLoader module
   *
   * @property {import("three").Scene} scene - The main scene object
   * @property {import("three").PerspectiveCamera} camera - The main camera with 75° FOV
   * @property {import("three").WebGLRenderer} renderer - WebGL renderer with antialiasing
   * @property {OrbitControls} controls - Camera controls for user interaction
   *
   * @returns Function - Cleanup function that removes event listeners and disposes of the renderer
   * @throws Error - Throws an error if model loading fails
   */
  const initScene = () => {
    showCentralLoadingSpinner = true;

    let modelCenter = null;
    let modelRadius = null;
    const aspect = container.clientWidth / container.clientHeight;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });

    scene.background = new THREE.Color(0xE0E0E0);

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 5, 5).normalize();
    scene.add(directionalLight);

    // Initialize OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.25;
    controls.screenSpacePanning = false;

    // Function for updating the camera position
    const updateCameraPosition = () => {
      if (modelCenter && modelRadius) {
        const fov = camera.fov * (Math.PI / 180);
        const cameraDistance = (modelRadius * 2.5) / Math.tan(fov / 2);

        camera.position.set(
          modelCenter.x,
          modelCenter.y + modelRadius * 0.5,
          modelCenter.z + cameraDistance,
        );
        camera.lookAt(modelCenter);

        controls.target.copy(modelCenter);
        controls.update();
      }
    };

    // Load the GLB model
    const loader = new GLTFLoader();
    loader.load(url?.href ?? url, (gltf) => {
      showCentralLoadingSpinner = false;
      scene.add(gltf.scene);

      // Calculate the model's bounding sphere
      const box = new THREE.Box3().setFromObject(gltf.scene);
      const sphere = new THREE.Sphere();
      box.getBoundingSphere(sphere);

      // Save center and radius for later use
      modelCenter = sphere.center.clone();
      modelRadius = sphere.radius;

      // Configure zoom limits for OrbitControls
      controls.minDistance = modelRadius * 1.5;
      controls.maxDistance = modelRadius * 4;
      controls.minPolarAngle = Math.PI / 4;
      controls.maxPolarAngle = Math.PI * 3 / 4;

      // Update camera home position
      updateCameraPosition();

      renderer.render(scene, camera);
    }, undefined, (error) => {
      console.error("An error happened:", error);
      showCentralLoadingSpinner = false;
      available = false;
    });

    const animate = function () {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    resizeContainerModelObserver?.disconnect();
    resizeContainerModelObserver = new ResizeObserver(() => {
      requestAnimationFrame(() => {
        camera.aspect = container.clientWidth / container.clientHeight; // newAspect
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
        updateCameraPosition(); // Recalculate camera position in the resize
      });
    });

    resizeContainerModelObserver.observe(container);
  };

  /**
   * Cleans up and disposes of all THREE.js scene resources including meshes, materials, geometries,
   * and the WebGL renderer. Also removes the canvas element from the DOM.
   *
   * @param {THREE.Scene} scene - The THREE.js scene to clean
   * @param {THREE.WebGLRenderer} renderer - The THREE.js renderer to dispose
   * @param {HTMLElement} container - The container element holding the canvas
   *
   * @throws {Error} If scene, renderer or container are not properly initialized
   */
  const cleanScene = () => {
    if (!scene) return;

    // Cleans all objects in the scene
    while (scene.children.length > 0) {
      const object = scene.children[0];
      if (object.type === "Mesh") {
        object.geometry.dispose();
        object.material.dispose();
      }
      scene.remove(object);
    }

    // Clean the renderer
    renderer.dispose();

    // Removes the existing canvas
    if (container.firstChild) {
      container.removeChild(container.firstChild);
    }
  };


  /**
   * Clears the scene and initializes it
   * @returns void
   */
  export const reloadScene = () => {
    cleanScene();
    initScene();
  };

  /**
   * Indicates whether it is supported by the device
   * @returns boolean
   */
  const isFullScreenSupported = () => {
    return "fullscreenEnabled" in document
      || "mozFullScreenEnabled" in document
      || "webkitFullscreenEnabled" in document
      || "msFullscreenEnabled" in document;
  };

  const toggleFullScreen = async () => {
    isFullScreen = !isFullScreen;
    isFullScreen
      ? await requestFullScreen()
      : await exitFullScreen();
  };

  /**
   * Request fullscreen in the given element.
   * @returns Promise<void>
   */
  const requestFullScreen = async () => {
    if (!isFullScreenSupported) return;

    if (container.requestFullscreen) {
      await container.requestFullscreen();
    } else if (container.msRequestFullscreen) {
      await container.msRequestFullscreen();
    } else if (container.mozRequestFullScreen) {
      await container.mozRequestFullScreen();
    } else if (container.webkitRequestFullscreen) {
      await container.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
    }
  };

  /**
   * Request fullscreen in the given element.
   * @returns Promise<void>
   */
  const exitFullScreen = async () => {
    if (!isFullScreenSupported()) return;

    // TODO. Search which is the 'exitFullScreen' prop from 'moz' (if exists)
    if (document.exitFullscreen) {
      await document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      await document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      await document.msExitFullscreen();
    }
  };

  $effect(() => {
    if (url && container) reloadScene();
  });
</script>

<div class="three-viewer-container">
  <div bind:this={container} class="inject-model">
    {#if isFullScreenSupported() && available && !showCentralLoadingSpinner}
      <div class="btn-fullscreen">
        <BaseButton outline size="sm" type="primary" onclick={toggleFullScreen}>
          <i class="fas fa-expand"></i>
        </BaseButton>
      </div>
    {/if}
  </div>
  {#if available}
    {#if showCentralLoadingSpinner}
      <div class="central-btn" in:fade={{duration: 200}}>
        <span class="fa-3x fa-fw fas fa-spinner fa-spin text-white"></span>
      </div>
    {/if}
  {:else}
    <div class="d-flex align-items-center justify-content-center no-available-model">
      <div class="d-flex align-items-center justify-content-center flex-column">
        <i class="fal fa-link-slash fa-fw fa-{iconSize}"></i>
        {#if !hideNotAvailableLabel}
          <span class="pt-4">{$t('component.three-viewer.not-available')}</span>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .three-viewer-container {
    width: 100%;
    position: relative;
    margin: 1rem;
  }

  .inject-model {
    width: 100%;
    height: 200px;
  }

  .central-btn {
    cursor: pointer;
    position: absolute;
    top: 50%;
    left: 50%;
    color: #F3F3F3;
    border-radius: 50%;
    padding: 1.4rem 1rem;
    transform: translate(-50%, -50%);
    backdrop-filter: blur(0.6rem);
    background-color: rgba(109, 109, 109, 0.2);
  }

  .no-available-model {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
  }

  .btn-fullscreen {
    position: absolute;
    top: 0;
    right: 0;
    margin: 0.5rem 0.5rem 0 0;
    cursor: pointer;
  }

</style>
