'use client';
import { useState, useEffect, useRef } from 'react';
import { AgentCollaboration } from './AgentCollaboration';

// A simplified 64x32 binary world map to dictate Land (1) vs Water (0)
const WORLD_MAP = [
  "0000000000000000000000000000000000000000000000000000000000000000",
  "0000000000000000000000000000000000000000000000000000000000000000",
  "0000000111111100000000000011111111111100000000000000000000000000",
  "0000011111111111000000000111111111111111100000000000000000000000",
  "0000111111111111100000001111111111111111110000000000000000000000",
  "0000011111111111000000000111111111111111111000000000000000000000",
  "0000001111111100000000000011111111111111111100000000000000000000",
  "0000000111111000000000000001111111111111111100000000000000000000",
  "00000000111000000000000000001111111111111110000000011100000000",
  "00000000111000000000000000000111111111111000000000111110000000",
  "00000000011000000000000000000011111111100000000000111000000000",
  "00000000011000000000000000000001111110000000000000111000000000",
  "00000000001000000000000000000000111000000000000000000000000000",
  "00000000001000000000000000000000010000000000000000000000000000",
  "00000000000000000000000000000000000000000000000000000000000000",
  "00000000000000000000000000000000000000000000000000000000000000"
];

export default function NiyatiLanding() {
  const [isProductsHovered, setIsProductsHovered] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Scroll Listener for Navbar Detachment
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 40);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 3D "Outside the Globe" ASCII Projection with Mouse Tracking
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = window.innerWidth;
    let height = window.innerHeight * 0.8;
    canvas.width = width;
    canvas.height = height;

    const points: { x: number; y: number; z: number; isLand: boolean; isNode: boolean }[] = [];

    // Scale the sphere to be visible as a "hemisphere" at the bottom
    const sphereRadius = width < 768 ? width * 0.6 : width * 0.4;
    const focalLength = 1500;
    const zOffset = 2200;

    // Generate latitude/longitude grid and map it to the 16x64 WORLD_MAP
    const latLines = 50;
    const lonLines = 100;

    for (let i = 0; i <= latLines; i++) {
      const theta = (i / latLines) * Math.PI;
      const mapRowIndex = Math.floor((i / latLines) * 15);

      for (let j = 0; j <= lonLines; j++) {
        const phi = (j / lonLines) * Math.PI * 2;
        const mapColIndex = Math.floor((j / lonLines) * 63);

        const isLand = WORLD_MAP[mapRowIndex]?.[mapColIndex] === '1';
        // Flag some random land points as special active "nodes"
        const isNode = isLand && Math.random() > 0.95;

        const x = sphereRadius * Math.sin(theta) * Math.cos(phi);
        const y = sphereRadius * Math.sin(theta) * Math.sin(phi);
        const z = sphereRadius * Math.cos(theta);

        points.push({ x, y, z, isLand, isNode });
      }
    }

    let globalRotation = 0;
    let mouseOffsetX = 0;
    let mouseOffsetY = 0;
    let currentOffsetX = 0;
    let currentOffsetY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      // Primary axis: Allow full tracking horizontally (Y-axis spin)
      mouseOffsetX = ((e.clientX / window.innerWidth) - 0.5) * Math.PI * 0.8;
      // Secondary axes: Heavily limit vertical tracking (X-axis tilt)
      mouseOffsetY = ((e.clientY / window.innerHeight) - 0.5) * 0.15;
    };

    window.addEventListener('mousemove', handleMouseMove);

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      // Auto-spin logic
      globalRotation -= 0.002;

      // Smooth lerp towards mouse position
      currentOffsetX += (mouseOffsetX - currentOffsetX) * 0.05;
      currentOffsetY += (mouseOffsetY - currentOffsetY) * 0.05;

      const finalAngleY = globalRotation + currentOffsetX;
      const finalAngleX = 0.05 + currentOffsetY; // Very slight base tilt so we're primarily looking at the equator
      const finalAngleZ = currentOffsetX * 0.05;  // Very slight roll based on horizontal movement

      // PERFORMANCE OPTIMIZATION: 
      // Pre-calculate all trig math for this frame once (Saves 30,000+ calculations per tick)
      const cosY = Math.cos(finalAngleY);
      const sinY = Math.sin(finalAngleY);
      const cosX = Math.cos(finalAngleX);
      const sinX = Math.sin(finalAngleX);
      const cosZ = Math.cos(finalAngleZ);
      const sinZ = Math.sin(finalAngleZ);
      const halfWidth = width / 2;

      // Swap to standard for-loop to avoid callback overhead
      for (let i = 0; i < points.length; i++) {
        const point = points[i];

        // 1. Rotate around Y (Global Spin + Primary Horizontal Tracking)
        let rot1X = point.x * cosY - point.z * sinY;
        let rot1Z = point.x * sinY + point.z * cosY;
        let rot1Y = point.y;

        // 2. Rotate around X (Vertical Tracking)
        let rot2Y = rot1Y * cosX - rot1Z * sinX;
        let rot2Z = rot1Y * sinX + rot1Z * cosX;
        let rot2X = rot1X;

        // 3. Rotate around Z (Parallax Roll)
        let finalX = rot2X * cosZ - rot2Y * sinZ;
        let finalY = rot2X * sinZ + rot2Y * cosZ;
        let finalZ = rot2Z;

        // "Outside" view: we render points on the front hemisphere (closer to camera, finalZ < 0)
        if (finalZ < 0) {
          const scale = focalLength / (zOffset + finalZ); // Push perspective way back

          const px = halfWidth + finalX * scale;
          const py = height + finalY * scale; // Centered at the very bottom edge

          if (py < height && py > 0 && px > 0 && px < width) {

            if (point.isNode) {
              // Draw a solid circle for "active nodes"
              ctx.beginPath();
              ctx.fillStyle = `rgba(0, 91, 82, ${0.8 + scale * 0.2})`;
              ctx.arc(px, py, 4 * scale, 0, Math.PI * 2);
              ctx.fill();
            } else {
              ctx.font = `bold ${Math.max(6, 14 * scale)}px monospace`;
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";

              if (point.isLand) {
                // High contrast Teal #
                ctx.fillStyle = `rgba(0, 91, 82, ${0.5 + scale * 0.5})`;
                ctx.fillText('#', px, py);
              } else {
                // Extremely Faded Teal #
                ctx.fillStyle = `rgba(0, 91, 82, ${0.05 + scale * 0.1})`;
                ctx.fillText('#', px, py);
              }
            }
          }
        }
      } // End of high-performance loop
      requestAnimationFrame(animate);
    };
    animate();

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight * 0.8;
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className="relative min-h-[200vh] bg-[#f7faf9] text-[#005b52] font-sans transition-colors duration-500">

      {/* Dynamic Navbar: Flat & Transparent -> Floating Pill */}
      <nav className={`fixed z-50 left-1/2 -translate-x-1/2 transition-all duration-500 ease-[cubic-bezier(0.25,1,0.5,1)] flex items-center justify-between
        ${isScrolled
          ? 'top-6 w-[95%] max-w-5xl rounded-full bg-[#04221f] text-white shadow-2xl px-8 py-3'
          : 'top-0 w-full max-w-[100vw] rounded-none bg-transparent text-[#005b52] px-10 py-6'
        }`}
      >
        {/* Brand / Logo */}
        <div className="flex items-center">
          <span className="font-serif text-3xl font-bold tracking-tight">Niyati</span>
        </div>

        {/* Navigation Links */}
        <div className="hidden md:flex gap-8 text-sm font-medium tracking-wide items-center">
          <a href="#industries" className={`transition-colors ${isScrolled ? 'hover:text-[#dbf226]' : 'hover:text-[#04221f]/70'}`}>Industries</a>

          {/* Dropdown Trigger */}
          <div
            className="relative h-full flex items-center"
            onMouseEnter={() => setIsProductsHovered(true)}
            onMouseLeave={() => setIsProductsHovered(false)}
          >
            <button className={`flex items-center gap-1 transition-colors py-2 ${isScrolled ? 'hover:text-[#dbf226]' : 'hover:text-[#04221f]/70'}`}>
              Products
              <svg className={`w-4 h-4 transition-transform ${isProductsHovered ? 'rotate-180' : ''} ${isScrolled && isProductsHovered ? 'text-[#dbf226]' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>

            {/* The Dropdown Mega-Menu Card */}
            <div className={`absolute top-full left-1/2 -translate-x-1/2 pt-4 transition-all duration-300 ease-out origin-top ${isProductsHovered ? 'opacity-100 scale-100 pointer-events-auto' : 'opacity-0 scale-95 pointer-events-none'} ${!isScrolled && isProductsHovered ? 'mt-4' : ''}`}>
              {/* Force white text inside dropdown card even if navbar is transparent light-mode */}
              <div className="w-[450px] bg-[#04221f] text-white rounded-3xl p-6 shadow-2xl border border-white/5 flex gap-8 relative overflow-hidden text-left">

                {/* Subtle highlight effect in the dropdown background */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-[#dbf226] rounded-full blur-[80px] opacity-10"></div>

                {/* Column 1 */}
                <div className="flex-1 flex flex-col gap-5 relative z-10">
                  <a href="#" className="flex items-center gap-3 hover:text-[#dbf226] group">
                    <span className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-[#dbf226]/20 transition-colors">🔍</span>
                    <div>
                      <div className="font-bold">The Ghost Signal</div>
                      <div className="text-xs text-white/50">E-Way Bill vs IRN</div>
                    </div>
                  </a>
                  <a href="#" className="flex items-center gap-3 hover:text-[#dbf226] group">
                    <span className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-[#dbf226]/20 transition-colors">🕸️</span>
                    <div>
                      <div className="font-bold">Spider Web Engine</div>
                      <div className="text-xs text-white/50">Community Detection</div>
                    </div>
                  </a>
                </div>

                {/* Column 2 */}
                <div className="flex-1 flex flex-col gap-5 relative z-10">
                  <a href="#" className="flex items-center gap-3 hover:text-[#dbf226] group">
                    <span className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-[#dbf226]/20 transition-colors">💸</span>
                    <div>
                      <div className="font-bold">Payment Gap</div>
                      <div className="text-xs text-white/50">GSTR-1 vs 3B</div>
                    </div>
                  </a>
                  <a href="#" className="flex items-center gap-3 hover:text-[#dbf226] group">
                    <span className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center group-hover:bg-[#dbf226]/20 transition-colors">🤖</span>
                    <div>
                      <div className="font-bold">Explainable AI</div>
                      <div className="text-xs text-white/50">EBM Narratives</div>
                    </div>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <a href="#resources" className={`transition-colors ${isScrolled ? 'hover:text-[#dbf226]' : 'hover:text-[#04221f]/70'}`}>Resources</a>
        </div>

        {/* Right CTA */}
        <div className="flex items-center gap-6">
          <a href="/login" className={`text-sm font-semibold transition-colors ${isScrolled ? 'hover:text-[#dbf226]' : 'hover:text-[#04221f]/70'}`}>Log In</a>
          <a href="#contact" className={`text-sm font-semibold transition-colors ${isScrolled ? 'hover:text-[#dbf226]' : 'hover:text-[#04221f]/70'}`}>Contact Us</a>
          <button className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors shadow-inner
            ${isScrolled
              ? 'bg-[#113a35] hover:bg-[#dbf226] hover:text-[#04221f]'
              : 'bg-[#005b52]/10 hover:bg-[#005b52] hover:text-white'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative h-screen flex flex-col items-center justify-start pt-24 md:pt-32 overflow-hidden">

        <div className="relative z-10 flex flex-col items-center text-center px-4">

          <div className={`mb-8 px-5 py-2 rounded-full border text-sm font-semibold tracking-wide shadow-sm flex items-center gap-3 transition-colors ${isScrolled ? 'bg-white border-[#005b52]/10' : 'bg-[#005b52]/5 border-[#005b52]/10'}`}>
            <span className="bg-[#dbf226] text-[#005b52] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
              System Live
            </span>
            Forensic Multi-Agent Intelligence Layer
          </div>

          <h1 className="font-serif text-6xl md:text-8xl lg:text-[7rem] font-bold tracking-tight mb-6 text-[#005b52]">
            Niyati
          </h1>

          <p className="text-lg md:text-xl text-[#005b52]/80 max-w-3xl mb-12 font-medium leading-relaxed">
            Real-time GST Intelligence Platform. Detect circular trading loops, isolate payment gaps, and secure your supply chain with explainable AI.
          </p>

          <button className="bg-[#04221f] text-white font-bold text-lg px-8 py-4 rounded-full shadow-[0_10px_30px_rgba(4,34,31,0.3)] hover:bg-[#dbf226] hover:text-[#04221f] hover:-translate-y-1 transition-all duration-300">
            Run Pre-Audit Safety Check
          </button>
        </div>

        {/* ASCII Outside-Globe Hemisphere Canvas anchored to bottom */}
        <div className="absolute bottom-0 left-0 w-full h-[80vh] mask-image-to-top opacity-90 pointer-events-none">
          <canvas ref={canvasRef} className="w-full h-full block" />
        </div>
      </section>

      {/* Agent Collaboration Section */}
      <AgentCollaboration />

      {/* CSS Gradation Mask */}
      <style dangerouslySetInnerHTML={{
        __html: `
        .mask-image-to-top {
          mask-image: linear-gradient(to top, rgba(247,250,249,1) 5%, rgba(247,250,249,0) 80%);
          -webkit-mask-image: linear-gradient(to top, rgba(247,250,249,1) 5%, rgba(247,250,249,0) 80%);
        }
      `}} />
    </div>
  );
}
