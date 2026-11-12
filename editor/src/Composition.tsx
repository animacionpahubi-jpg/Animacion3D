import {Composition} from 'remotion';
import {AtrapaLaGota} from './AtrapaLaGota';
import {TuPuedes} from './TuPuedes';
import {TuPuedesVoces} from './TuPuedesVoces';

export const MyComposition = () => {
	return (
		<>
			<Composition id="TuPuedesVoces" component={TuPuedesVoces} durationInFrames={632} fps={24} width={1080} height={1920} />
			<Composition id="TuPuedes" component={TuPuedes} durationInFrames={625} fps={24} width={1080} height={1920} />
			<Composition id="AtrapaLaGota" component={AtrapaLaGota} durationInFrames={596} fps={24} width={1080} height={1920} />
		</>
	);
};
