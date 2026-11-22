from backend.timeline.timeline_schema import TimelineSpec


class TimelineController:

    def __init__(self, timeline: TimelineSpec):
        self.timeline = timeline
        self.validate()

    def validate(self) -> None:
        track_ids = {
            track.id for track in self.timeline.tracks
        }

        if len(track_ids) != len(self.timeline.tracks):
            raise ValueError("Duplicate timeline track ID")

        clip_ids = set()

        for clip in self.timeline.clips:
            if clip.id in clip_ids:
                raise ValueError(
                    f"Duplicate timeline clip ID: {clip.id}"
                )

            clip_ids.add(clip.id)

            if clip.track_id not in track_ids:
                raise ValueError(
                    f"Unknown track ID: {clip.track_id}"
                )

            if clip.end > self.timeline.duration:
                raise ValueError(
                    f"Clip exceeds timeline duration: {clip.id}"
                )

    def get_active_clips(self, time: float) -> list:
        if time < 0 or time >= self.timeline.duration:
            return []

        return [
            clip
            for clip in self.timeline.clips
            if clip.start <= time < clip.end
        ]

    def get_clip_progress(self, clip_id: str, time: float) -> float:
        clip = next(
            (
                item
                for item in self.timeline.clips
                if item.id == clip_id
            ),
            None,
        )

        if clip is None:
            raise ValueError(f"Clip not found: {clip_id}")

        if time < clip.start or time >= clip.end:
            return 0.0

        elapsed = time - clip.start

        return elapsed / clip.duration

    def get_frame_time(self, frame_index: int) -> float:
        if frame_index < 0:
            raise ValueError("Frame index cannot be negative")

        total_frames = int(
            self.timeline.duration * self.timeline.fps
        )

        if frame_index >= total_frames:
            raise ValueError("Frame index exceeds timeline")

        return frame_index / self.timeline.fps
