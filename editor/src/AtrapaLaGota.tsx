import {Audio, Video} from '@remotion/media';
import {
	AbsoluteFill,
	Freeze,
	Img,
	interpolate,
	Sequence,
	Series,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';

// «¡Atrapa la gota!» v6 — 3 planos Kling 3.0 Pro (1176x1764) en 1080x1920 a 24 fps.
// Todos los planos usan el MISMO encuadre (sin saltos en los cortes).
// Los tramos con defectos cortos (gota estirada en B, pico que toca el gorro en C) se ACELERAN a 3x en vez de cortarse:
// el movimiento sigue continuo y el defecto dura ~0,3 s.
// El audio (public/audio.wav) lo genera src/audio_cap1v6.py con estos mismos tiempos.

const ENCUADRE = '20% 50%'; // posición horizontal del recorte 2:3 → 9:16 (igual en todos los planos)

const Plano: React.FC<{
	readonly src: string;
	readonly desde: number;
	readonly velocidad?: number;
}> = ({src, desde, velocidad = 1}) => (
	<Video
		src={staticFile(src)}
		trimBefore={desde}
		playbackRate={velocidad}
		muted
		objectFit="cover"
		style={{width: '100%', height: '100%', objectPosition: ENCUADRE}}
	/>
);

const Titulo: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = frame / fps;
	const opacidad = interpolate(t, [0.1, 0.45, 2.4, 2.8], [0, 1, 1, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const rebote = -40 * Math.exp(-8 * t) * Math.cos(14 * t);
	return (
		<Img
			src={staticFile('titulo.png')}
			style={{position: 'absolute', inset: 0, width: '100%', opacity: opacidad, translate: `0px ${rebote}px`}}
		/>
	);
};

const FundidoFinal: React.FC = () => {
	const frame = useCurrentFrame();
	const {durationInFrames, fps} = useVideoConfig();
	const opacidad = interpolate(frame, [durationInFrames - 0.8 * fps, durationInFrames], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	return <AbsoluteFill style={{backgroundColor: 'black', opacity: opacidad}} />;
};

export const AtrapaLaGota: React.FC = () => {
	return (
		<AbsoluteFill style={{backgroundColor: 'black'}}>
			<Series>
				<Series.Sequence name="A · gota y picada al charco" durationInFrames={120}>
					<Plano src="cap1-A3.mp4" desde={0} />
				</Series.Sequence>
				<Series.Sequence name="B · mira la flor" durationInFrames={91}>
					<Plano src="cap1-B2.mp4" desde={0} />
				</Series.Sequence>
				<Series.Sequence name="B · gota cae (3x)" durationInFrames={8}>
					<Plano src="cap1-B2.mp4" desde={91} velocidad={3} />
				</Series.Sequence>
				<Series.Sequence name="B · risa y llega mamá" durationInFrames={125}>
					<Plano src="cap1-B2.mp4" desde={115} />
				</Series.Sequence>
				<Series.Sequence name="C · mamá se acerca" durationInFrames={101}>
					<Plano src="cap1-C2.mp4" desde={0} />
				</Series.Sequence>
				<Series.Sequence name="C · se junta (3x)" durationInFrames={6}>
					<Plano src="cap1-C2.mp4" desde={101} velocidad={3} />
				</Series.Sequence>
				<Series.Sequence name="C · abrazo" durationInFrames={120}>
					<Plano src="cap1-C2.mp4" desde={119} />
				</Series.Sequence>
				<Series.Sequence name="C · abrazo congelado" durationInFrames={25}>
					<Freeze frame={0}>
						<Plano src="cap1-C2.mp4" desde={238} />
					</Freeze>
				</Series.Sequence>
			</Series>
			<Sequence name="Título" durationInFrames={70}>
				<Titulo />
			</Sequence>
			<FundidoFinal />
			{/* el wav es mono a −18 LUFS; al pasar a estéreo sube ~3 dB → 0,7 lo deja en −18 */}
			<Audio src={staticFile('audio.wav')} volume={0.7} />
		</AbsoluteFill>
	);
};
