from backend.scenes.scene_schema import SceneSpec
from backend.timeline.timeline_schema import (
    TimelineClip,
    TimelineClipType,
    TimelineSpec,
    TimelineTrack,
    TimelineTrackType,
)


class TimelineBuilder:

    def build(self, scene: SceneSpec) -> TimelineSpec:
        tracks = []
        clips = []

        # Character tracks
        for character in scene.characters:
            track_id = f"character_{character.id}"

            track_clips = []
            current_time = 0.0

            for action_index, action in enumerate(
                character.actions
            ):
                iteration_duration = (
                    action.duration / action.repeat
                )

                for repeat_index in range(action.repeat):
                    clip = TimelineClip(
                        id=(
                            f"{character.id}_"
                            f"{action_index}_"
                            f"{repeat_index}"
                        ),
                        track_id=track_id,
                        target_id=character.id,
                        clip_type=TimelineClipType.ACTION,
                        start=current_time,
                        duration=iteration_duration,
                        engine=action.engine,
                        action_name=action.name,
                        asset_path=character.asset_path,
                        params=action.params,
                    )

                    track_clips.append(clip)
                    clips.append(clip)

                    current_time += iteration_duration

            tracks.append(
                TimelineTrack(
                    id=track_id,
                    track_type=TimelineTrackType.CHARACTER,
                    target_id=character.id,
                    clips=track_clips,
                )
            )

        # Background track
        if scene.background:
            background_clip = TimelineClip(
                id=f"{scene.scene_id}_background",
                track_id="background",
                target_id="background",
                clip_type=TimelineClipType.BACKGROUND,
                start=0,
                duration=scene.duration,
                params={
                    "background": scene.background,
                },
            )

            clips.append(background_clip)

            tracks.append(
                TimelineTrack(
                    id="background",
                    track_type=TimelineTrackType.BACKGROUND,
                    target_id="background",
                    clips=[background_clip],
                )
            )

        return TimelineSpec(
            scene_id=scene.scene_id,
            duration=scene.duration,
            fps=scene.fps,
            width=scene.width,
            height=scene.height,
            tracks=tracks,
            clips=clips,
        )
