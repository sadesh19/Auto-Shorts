import json

keywords = [
    "ai",
    "machine learning",
    "important",
    "tutorial"
]

with open("transcript.json", "r") as file:
    transcript = json.load(file)

def score_clip(segment):

    score = 0

    text = segment["text"].lower()

    for keyword in keywords:
        if keyword in text:
            score += 10

    duration = segment["end"] - segment["start"]

    if 15 <= duration <= 60:
        score += 5

    return score


for segment in transcript:
    segment["score"] = score_clip(segment)

ranked = sorted(
    transcript,
    key=lambda x: x["score"],
    reverse=True
)

selected = []

for clip in ranked:

    overlap = False

    for chosen in selected:

        if not (
            clip["end"] <= chosen["start"]
            or
            clip["start"] >= chosen["end"]
        ):
            overlap = True
            break

    if not overlap:
        selected.append(clip)

    if len(selected) == 3:
        break

final_clips = []

for clip in selected:
    final_clips.append({
        "start": clip["start"],
        "end": clip["end"]
    })

with open("output.json", "w") as file:
    json.dump(final_clips, file, indent=4)

print("Selected Clips:")
print(final_clips)