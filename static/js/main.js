/* ==========================================================================
   ENTRIX II — main.js (Stage 2)
   - Loading sequence orchestration (first-visit vs. returning-visit timing)
   - Navigation (scroll state, mobile menu)
   - 3D hero scene (lazy-loaded, reduced-motion aware)
   - Project card tilt effect (3D perspective on hover)
   ========================================================================== */

(function () {
  "use strict";

  const prefersReducedMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isTouch = window.matchMedia && window.matchMedia("(pointer: coarse)").matches;

  /* ------------------------------------------------------------------ */
  /* Loading sequence                                                    */
  /* ------------------------------------------------------------------ */

  function runLoader() {
    const loader = document.getElementById("loader");
    const fill = document.querySelector(".loader-bar-fill");
    const hero = document.getElementById("hero");
    if (!loader) return;

    const alreadyVisited = sessionStorage.getItem("entrix_visited") === "1";
    const duration = prefersReducedMotion ? 0 : alreadyVisited ? 350 : 900;

    if (fill) {
      requestAnimationFrame(() => {
        fill.style.transition = `width ${Math.max(duration, 1)}ms linear`;
        fill.style.width = "100%";
      });
    }

    const glitchAt = Math.max(duration - 300, 0);
    window.setTimeout(() => loader.classList.add("loader-glitch"), glitchAt);

    window.setTimeout(() => {
      loader.classList.add("loader-hide");
      if (hero) hero.classList.add("hero-ready");
      sessionStorage.setItem("entrix_visited", "1");
      window.setTimeout(() => {
        loader.setAttribute("hidden", "");
        initHeroScene();
        initCardTilt();
      }, prefersReducedMotion ? 0 : 300);
    }, duration);
  }

  /* ------------------------------------------------------------------ */
  /* Navigation                                                          */
  /* ------------------------------------------------------------------ */

  function initNav() {
    const nav = document.getElementById("site-nav");
    const toggle = document.getElementById("nav-toggle");
    const mobileNav = document.getElementById("mobile-nav");

    const onScroll = () => {
      if (!nav) return;
      nav.classList.toggle("nav-scrolled", window.scrollY > 24);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    if (toggle && mobileNav) {
      toggle.addEventListener("click", () => {
        const open = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!open));
        mobileNav.classList.toggle("open", !open);
        document.body.style.overflow = open ? "" : "hidden";
      });

      mobileNav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
          toggle.setAttribute("aria-expanded", "false");
          mobileNav.classList.remove("open");
          document.body.style.overflow = "";
        });
      });
    }
  }

  /* ------------------------------------------------------------------ */
  /* Project card tilt (3D perspective on hover)                        */
  /* ------------------------------------------------------------------ */

  function initCardTilt() {
    if (prefersReducedMotion || isTouch) return;

    const cards = document.querySelectorAll(".project-card");
    cards.forEach((card) => {
      const frame = card.querySelector(".device-frame");
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        const rotateX = y * -6;   // up/down
        const rotateY = x * 8;    // left/right
        card.style.transform =
          `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        if (frame) {
          frame.style.transform =
            `perspective(800px) rotateX(${rotateX * 0.3}deg) rotateY(${rotateY * 0.3}deg)`;
        }
      });
      card.addEventListener("mouseleave", () => {
        card.style.transform = "";
        if (frame) frame.style.transform = "";
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Hero 3D scene — lazy-loaded, GPU-friendly, mouse-parallax on desktop */
  /* ------------------------------------------------------------------ */

  let heroSceneStarted = false;

  async function initHeroScene() {
    if (heroSceneStarted) return;
    heroSceneStarted = true;

    const canvas = document.getElementById("hero-canvas");
    if (!canvas) return;

    if (prefersReducedMotion || isTouch) return;

    let THREE;
    try {
      THREE = await import("https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js");
    } catch (err) {
      return;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      42,
      canvas.clientWidth / canvas.clientHeight,
      0.1,
      100
    );
    camera.position.set(0, 0, 9);

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

    function resize() {
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    resize();
    window.addEventListener("resize", resize);

    scene.add(new THREE.AmbientLight(0x1a2030, 1.1));

    const key = new THREE.PointLight(0xffffff, 2.6, 30);
    key.position.set(4, 5, 6);
    scene.add(key);

    const rim = new THREE.PointLight(0x2f6fff, 6, 30);
    rim.position.set(-6, -2, -4);
    scene.add(rim);

    const rim2 = new THREE.PointLight(0x5fa8ff, 3, 20);
    rim2.position.set(0, -4, 4);
    scene.add(rim2);

    const group = new THREE.Group();
    scene.add(group);

    const chromeMat = new THREE.MeshStandardMaterial({
      color: 0x9aa4b2,
      metalness: 1,
      roughness: 0.28,
    });
    const chromeMatBright = new THREE.MeshStandardMaterial({
      color: 0xd7dce3,
      metalness: 1,
      roughness: 0.15,
    });

    const shardDefs = [
      { r: 1.6, mat: chromeMatBright, pos: [0, 0, 0], rot: [0.4, 0.6, 0.1] },
      { r: 0.6, mat: chromeMat, pos: [-2.1, 1.1, -1], rot: [0.9, 0.2, 0.4] },
      { r: 0.45, mat: chromeMat, pos: [2, -1.2, -0.6], rot: [0.2, 1.1, 0.2] },
      { r: 0.32, mat: chromeMatBright, pos: [1.3, 1.6, -1.4], rot: [0.6, 0.3, 0.8] },
    ];

    const shards = shardDefs.map((def) => {
      const geo = new THREE.OctahedronGeometry(def.r, 0);
      const mesh = new THREE.Mesh(geo, def.mat);
      mesh.position.set(...def.pos);
      mesh.rotation.set(...def.rot);
      group.add(mesh);
      return mesh;
    });

    const particleCount = 150;
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 20;
      positions[i + 1] = (Math.random() - 0.5) * 12;
      positions[i + 2] = (Math.random() - 0.5) * 10 - 2;
    }
    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x5fa8ff,
      size: 0.03,
      transparent: true,
      opacity: 0.5,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    let targetX = 0,
      targetY = 0;
    if (!isTouch) {
      window.addEventListener("pointermove", (e) => {
        targetX = (e.clientX / window.innerWidth - 0.5) * 2;
        targetY = (e.clientY / window.innerHeight - 0.5) * 2;
      });
    }

    let raf;
    const clock = new THREE.Clock();

    function animate() {
      raf = requestAnimationFrame(animate);
      const t = clock.getElapsedTime();

      group.rotation.y += 0.0025;
      group.rotation.x = Math.sin(t * 0.15) * 0.08;

      group.rotation.y += (targetX * 0.25 - group.rotation.y * 0.02) * 0.02;
      group.rotation.x += (-targetY * 0.15 - group.rotation.x * 0.02) * 0.02;

      shards.forEach((mesh, i) => {
        mesh.rotation.x += 0.001 * (i + 1);
        mesh.rotation.y += 0.0016 * (i + 1);
      });

      particles.rotation.y = t * 0.01;

      renderer.render(scene, camera);
    }

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        cancelAnimationFrame(raf);
      } else {
        animate();
      }
    });

    animate();
  }

  /* ------------------------------------------------------------------ */

  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("year") &&
      (document.getElementById("year").textContent = new Date().getFullYear());
    initNav();
    runLoader();
    if (prefersReducedMotion) {
      document.getElementById("hero") &&
        document.getElementById("hero").classList.add("hero-ready");
    }
  });
})();