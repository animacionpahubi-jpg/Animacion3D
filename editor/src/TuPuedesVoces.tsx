import {Audio, Video} from '@remotion/media';
import {AbsoluteFill, Freeze, Img, interpolate, Sequence, Series, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// «¡TÚ PUEDES!» CON VOCES (Kling audio nativo en español en P1, P4 y P5; audio y subtítulos: src/cap2v_textos_audio.py) — 5 planos Kling 3.0 Pro de 5 s (1176x1764) en 1080x1920 a 24 fps, mismo encuadre en todos.
// Tramos con defectos cortos ACELERADOS (no cortados): P2 el bebé cruza delante de mamá; P5 pico cerca de la cara.
// P3b (sin rebote): se levanta aturdido y el mareo empieza dentro del plano (causa visible = la caída). Textos: título/¡YO PUEDO!/cierre en estilo logo Pahubi; onomatopeyas y símbolos (¡PUM!, ¿?, foco de idea, ! de sorpresa de mamá) en estilo cómic blanco
// Audio y letreros: src/cap2_textos_audio.py (mismos tiempos).

const Plano: React.FC<{readonly src: string; readonly desde: number; readonly velocidad?: number}> = ({src, desde, velocidad = 1}) => (
	<Video src={staticFile(src)} trimBefore={desde} playbackRate={velocidad} muted objectFit="cover"
		style={{width: '100%', height: '100%', objectPosition: '50% 50%'}} />
);

const Letrero: React.FC<{readonly src: string; readonly sale?: number}> = ({src, sale}) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useVideoConfig();
	const t = frame / fps;
	const fin = sale ?? durationInFrames / fps;
	const opacidad = interpolate(t, [0.05, 0.3, fin - 0.35, fin], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const escala = 1 + 0.25 * Math.exp(-7 * t) * Math.cos(13 * t);
	return <Img src={staticFile(src)} style={{position: 'absolute', inset: 0, width: '100%', opacity: opacidad, scale: String(escala)}} />;
};


// Onomatopeyas 3D: estilo cómic blanco con sombra (assets/onomatopeyas/), entran con rebote, junto al personaje, en zona segura.
const Onomatopeya: React.FC<{readonly nombre: string; readonly x: number; readonly y: number; readonly ancho: number; readonly giro?: number}> = ({nombre, x, y, ancho, giro = 0}) => {
	const frame = useCurrentFrame();
	const {fps, durationInFrames} = useVideoConfig();
	const t = frame / fps;
	const escala = Math.min(1.12, 0.3 + 4 * t) * (1 + 0.12 * Math.exp(-8 * t) * Math.sin(20 * t));
	const opacidad = interpolate(frame, [0, 2, durationInFrames - 5, durationInFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<Img src={staticFile(`onomatopeyas/${nombre}.png`)}
			style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, translate: '0 -50%', rotate: `${giro}deg`, scale: String(escala), opacity: opacidad}} />
	);
};

const Sacudon: React.FC<{readonly children: React.ReactNode}> = ({children}) => {
	const frame = useCurrentFrame();
	const t = (frame - 175) / 24;
	const d = t >= 0 && t < 0.5 ? 18 * Math.exp(-9 * t) * Math.sin(55 * t) : 0;
	return <AbsoluteFill style={{translate: `${d * 0.6}px ${d}px`, scale: '1.03'}}>{children}</AbsoluteFill>;
};

export const TuPuedesVoces: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: 'black'}}>
		<Sacudon>
		<Series>
			<Series.Sequence name="P1 · asustado, llega mamá" durationInFrames={120}>
				<Plano src="cap3-voz-prueba.mp4" desde={0} />
			</Series.Sequence>
			<Series.Sequence name="P2 · se lanza" durationInFrames={46}>
				<Plano src="cap2-P2b.mp4" desde={0} />
			</Series.Sequence>
			<Series.Sequence name="P2 · cae (3x)" durationInFrames={8}>
				<Plano src="cap2-P2b.mp4" desde={46} velocidad={3} />
			</Series.Sequence>
			<Series.Sequence name="P2 · de panza en la hoja" durationInFrames={50}>
				<Plano src="cap2-P2b.mp4" desde={70} />
			</Series.Sequence>
			<Series.Sequence name="P3 · se levanta aturdido y se marea" durationInFrames={120}>
				<Plano src="cap2-P3b.mp4" desde={0} />
			</Series.Sequence>
			<Series.Sequence name="P4 · ¡vuela!" durationInFrames={120}>
				<Plano src="cap2v-P4.mp4" desde={0} />
			</Series.Sequence>
			<Series.Sequence name="P5 · bajan, «¡Lo lograste!», abrazo, «¡Te quiero, mami!»" durationInFrames={120}>
				<Plano src="cap2v-P5.mp4" desde={0} />
			</Series.Sequence>
			<Series.Sequence name="Cierre · abrazo congelado" durationInFrames={48}>
				<Freeze frame={0}>
					<Plano src="cap2v-P5.mp4" desde={119} />
				</Freeze>
			</Series.Sequence>
		</Series>
		</Sacudon>
		<Sequence name="Título ¡TÚ PUEDES!" durationInFrames={48}>
			<Letrero src="cap2-titulo.png" />
		</Sequence>
		<Sequence name="¡PUM! (cae)" from={174} durationInFrames={22}>
			<Onomatopeya nombre="pum" x={790} y={950} ancho={380} giro={-6} />
		</Sequence>
		<Sequence name="¿? (aturdido)" from={308} durationInFrames={16}>
			<Onomatopeya nombre="pregunta" x={240} y={620} ancho={170} giro={8} />
		</Sequence>
		<Sequence name="Sub: mamá «¡Tú puedes, hijo! ¡Vuela!»" from={46} durationInFrames={72}>
			<Letrero src="cap2-mama-dice.png" />
		</Sequence>
		<Sequence name="Foco: idea" from={366} durationInFrames={18}>
			<Onomatopeya nombre="foco-idea" x={290} y={760} ancho={250} giro={-4} />
		</Sequence>
		<Sequence name="Sub: bebé «¡Mami, mira! ¡Estoy volando!»" from={384} durationInFrames={84}>
			<Letrero src="cap2v-sub-mira.png" />
		</Sequence>
		<Sequence name="! mamá se sorprende" from={392} durationInFrames={24}>
			<Onomatopeya nombre="exclamacion-sola" x={900} y={560} ancho={110} giro={12} />
		</Sequence>
		<Sequence name="Sub: mamá «¡Lo lograste, mi amor!»" from={502} durationInFrames={48}>
			<Letrero src="cap2v-sub-lograste.png" />
		</Sequence>
		<Sequence name="Sub: bebé «¡Te quiero, mami!»" from={550} durationInFrames={36}>
			<Letrero src="cap2v-sub-tequiero.png" />
		</Sequence>
		<Sequence name="Envíaselo a quien amas" from={584} durationInFrames={48}>
			<Letrero src="cap2-cierre.png" sale={99} />
		</Sequence>
		{/* wav mono a −18 LUFS; al pasar a estéreo sube ~3 dB → 0,7 */}
		<Audio src={staticFile('cap2v-audio.wav')} volume={0.62} />
	</AbsoluteFill>
);
