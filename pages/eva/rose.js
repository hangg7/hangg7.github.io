const vshader = `
varying vec3 vertex_position;

void main() {
  vertex_position = position;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;
const fshader = `
uniform vec2 iMouse;
uniform vec2 iResolution;

varying vec3 vertex_position;

// ray marching
const int max_iterations = 128;
const float stop_threshold = 0.01;
const float grad_step = 0.01;
const float clip_far = 10.0;

// math
const float PI = 3.14159265359;
const float PI2 = 6.28318530718;
const float DEG_TO_RAD = PI / 180.0;

mat3 rotationXY(vec2 angle) {
	vec2 c = cos(angle);
	vec2 s = sin(angle);

	return mat3(
		c.y      ,  0.0, -s.y,
		s.y * s.x,  c.x,  c.y * s.x,
		s.y * c.x, -s.x,  c.y * c.x
	);
}

// distance function

float opI(float d1, float d2) {
  return max(d1, d2);
}

float opU(float d1, float d2) {
  return min(d1, d2);
}

float opS(float d1, float d2) {
  return max(-d1, d2);
}

float sdPetal(vec3 p, float s) {
  p = p * vec3(0.8, 1.5, 0.8) + vec3(0.1, 0.0, 0.0);
  vec2 q = vec2(length(p.xz), p.y);

  float lower = length(q) - 1.0;
  lower = opS(length(q) - 0.97, lower);
  lower = opI(lower, q.y);

  float upper = length((q - vec2(s, 0)) * vec2(1, 1)) + 1.0 - s;
  upper = opS(upper, length((q - vec2(s, 0)) * vec2(1, 1)) + 0.97 - s);
  upper = opI(upper, -q.y);
  upper = opI(upper, q.x - 2.0);

  float region = length(p - vec3(1.0, 0.0, 0.0)) - 1.0;

  return opI(opU(upper, lower), region);
}

float map(vec3 p) {
  float d = 1000.0, s = 2.0;
  mat3 r = rotationXY(vec2(0.1, PI2 * 0.618034));
  r = r * mat3(1.08,0.0,0.0 ,0.0,0.995,0.0, 0.0,0.0,1.08);
  for (int i = 0; i < 21; i++) {
      d = opU(d, sdPetal(p, s));
      p = r * p;
      p += vec3(0.0, -0.02, 0.0);
      s *= 1.05;
  }
  return d;
}

// get gradient in the world
vec3 gradient(vec3 pos) {
	const vec3 dx = vec3(grad_step, 0.0, 0.0);
	const vec3 dy = vec3(0.0, grad_step, 0.0);
	const vec3 dz = vec3(0.0, 0.0, grad_step);
	return normalize (
		vec3(
			map(pos + dx) - map(pos - dx),
			map(pos + dy) - map(pos - dy),
			map(pos + dz) - map(pos - dz)
		)
	);
}

// ray marching
float ray_marching(vec3 origin, vec3 dir, float start, float end) {
	float depth = start;
	for (int i = 0; i < max_iterations; i++) {
		float dist = map(origin + dir * depth);
		if (dist < stop_threshold) {
			return depth;
		}
		depth += dist * 0.3;
		if (depth >= end) {
			return end;
		}
	}
	return end;
}

const vec3 light_pos = vec3(20.0, 50.0, 20.0);
const vec3 fill_light = vec3(-15.0, 10.0, -10.0);

vec3 shading(vec3 v, vec3 n, vec3 eye) {
	vec3 ev = normalize(v - eye);

  // Petal color: soft gradient from deep rose center to warm pink edges
  float height = clamp(v.y * 0.5 + 0.5, 0.0, 1.0);
  float radial = clamp(length(v.xz) * 0.4, 0.0, 1.0);
  float blend = radial * 0.6 + height * 0.4;
  vec3 inner_color = vec3(0.55, 0.02, 0.08);
  vec3 outer_color = vec3(0.9, 0.15, 0.12);
  vec3 mat_color = mix(inner_color, outer_color, blend);

  // Key light
  vec3 vl = normalize(light_pos - v);
  float NdotL = dot(vl, n);
  float diffuse = NdotL * 0.5 + 0.5;

  // Fill light (soft, from below-left)
  vec3 fl = normalize(fill_light - v);
  float fill = max(dot(fl, n), 0.0) * 0.15;

  // Subsurface scattering — light passing through thin petals
  float sss = pow(clamp(dot(ev, vl), 0.0, 1.0), 3.0) * 0.35;
  vec3 sss_color = vec3(1.0, 0.2, 0.15) * sss;

  // Soft specular (lower exponent = broader, silkier highlight)
  vec3 h = normalize(vl - ev);
  float spec = pow(max(dot(n, h), 0.0), 16.0) * 0.25;

  // Rim lighting — warm glow at petal edges
  float fresnel = pow(1.0 - max(dot(n, -ev), 0.0), 4.0);
  vec3 rim = fresnel * 0.2 * vec3(1.0, 0.35, 0.3);

  // Ambient occlusion
  float ao = clamp(v.y * 0.5 + 0.65, 0.2, 1.0);

  vec3 result = (mat_color * (diffuse + fill) + sss_color + spec + rim) * ao;
  return result;
}

// get ray direction
vec3 ray_dir(float fov, vec2 size, vec2 pos) {
	vec2 xy = pos - size * 0.5;

	float cot_half_fov = tan((90.0 - fov * 0.5) * DEG_TO_RAD);
	float z = size.y * 0.5 * cot_half_fov;

	return normalize(vec3(xy, -z));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
	// default ray dir
	vec3 dir = ray_dir(45.0, iResolution.xy, fragCoord.xy);

	// default ray origin
	vec3 eye = vec3(0.0, 0.0, 5.0);

	// rotate camera — center around default angle with gentle offset from mouse
	vec2 baseAngle = vec2(-1.0, 1.0);
	vec2 mouseOffset = vec2(0.0);
	if (iMouse.x > 0.0) {
		// iMouse is normalized [0,1], map to offset range [-0.5, 0.5]
		mouseOffset = (iMouse.xy - 0.5) * vec2(0.5, -0.5);
	}
	mat3 rot = rotationXY(baseAngle + mouseOffset);

	dir = rot * dir;
	eye = rot * eye;

	// ray marching
	float depth = ray_marching(eye, dir, 0.0, clip_far);
  vec3 pos = eye + dir * depth;
  vec3 c;
  if (depth >= clip_far) {
    // Richer background: deep plum/wine gradient
    vec2 uv = fragCoord.xy / iResolution.xy;
    c = mix(vec3(0.15, 0.0, 0.08), vec3(0.25, 0.02, 0.12), uv.y * 0.8 + 0.1);
  }
  else {
    // shading
    vec3 n = gradient(pos);
    c = shading(pos, n, eye);
  }

  float r = 1.3 - length((fragCoord.xy / iResolution.xy) - 0.5) * 1.2;
  fragColor = vec4(c * r, 1.0);
}

void main() {
  mainImage(gl_FragColor, gl_FragCoord.xy);
}
`;

const canvas = document.getElementById("canvas");
const scene = new THREE.Scene();
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10);
const renderer = new THREE.WebGLRenderer({
  alpha: true,
  antialias: true,
});
const innerWidth = Math.min(window.innerWidth / 2, 480);
const innerHeight = Math.min(window.innerHeight / 2, 240);
renderer.setSize(innerWidth, innerHeight);
canvas.appendChild(renderer.domElement);

const clock = new THREE.Clock();
const geometry = new THREE.PlaneGeometry(2, 2);
const uniforms = {
  utime: {
    value: 0.0,
  },
  iMouse: {
    value: { x: 0.0, y: 0.0 },
  },
  iResolution: {
    value: { x: 0.0, y: 0.0 },
  },
  ucolor: {
    value: new THREE.Color(0xff0000),
  },
};
const material = new THREE.ShaderMaterial({
  uniforms: uniforms,
  vertexShader: vshader,
  fragmentShader: fshader,
});
const plane = new THREE.Mesh(geometry, material);
scene.add(plane);
camera.position.z = 1;

onWindowResize();

if ("ontouchstart" in window) {
  canvas.addEventListener("touchmove", move);
} else {
  window.addEventListener("resize", onWindowResize, false);
  canvas.addEventListener("mousemove", move);
  canvas.addEventListener("mouseleave", reset);
}

const mouseTarget = { x: 0.0, y: 0.0 };

animate();

function reset(event) {
  mouseTarget.x = 0.0;
  mouseTarget.y = 0.0;
}

function move(event) {
  const clientX = event.touches ? event.touches[0].clientX : event.clientX;
  const clientY = event.touches ? event.touches[0].clientY : event.clientY;
  const rect = renderer.domElement.getBoundingClientRect();
  mouseTarget.x = (clientX - rect.left) / rect.width;
  mouseTarget.y = (clientY - rect.top) / rect.height;
}

function animate() {
  requestAnimationFrame(animate);
  const lerp = 0.08;
  uniforms.iMouse.value.x += (mouseTarget.x - uniforms.iMouse.value.x) * lerp;
  uniforms.iMouse.value.y += (mouseTarget.y - uniforms.iMouse.value.y) * lerp;
  renderer.render(scene, camera);
  uniforms.utime.value = clock.getElapsedTime();
}

function onWindowResize(event) {
  const aspectRatio = window.innerWidth / window.innerHeight;
  let width;
  let height;
  if (aspectRatio >= 1) {
    width = 1;
    height = (window.innerHeight / window.innerWidth) * width;
  } else {
    width = aspectRatio;
    height = 1;
  }
  camera.left = -width;
  camera.right = width;
  camera.top = height;
  camera.bottom = -height;
  camera.updateProjectionMatrix();

  let innerWidth = Math.min(window.innerWidth / 2, 480);
  let innerHeight = Math.min(window.innerHeight / 2, 240);
  renderer.setSize(innerWidth, innerHeight);
  if (uniforms.iResolution !== undefined) {
    uniforms.iResolution.value.x = innerWidth;
    uniforms.iResolution.value.y = innerHeight;
  }
}
