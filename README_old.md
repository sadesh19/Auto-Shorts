# Week 1 - Clip Selection Module

## Project Overview

This project implements a basic clip selection system that processes transcript data and identifies the most relevant video clips based on scoring and ranking logic.

## Objective

Input: Transcript JSON

Process:

* Read transcript segments
* Score segments using keyword-based relevance
* Rank segments by score
* Remove overlapping clips
* Select top clips

Output:

* List of clip timestamps in (start, end) format

## Project Structure

Week1_ClipSelection/

├── transcript.json

├── clip_selector.py

├── output.json

├── requirements.txt

├── .gitignore

└── README.md

## Features

* Transcript JSON parsing
* Keyword-based clip scoring
* Clip ranking
* Non-overlapping clip selection
* JSON output generation

## How to Run

1. Install Python 3.x
2. Place transcript data in transcript.json
3. Run:

python clip_selector.py

4. Generated clips will be saved in output.json

## Sample Output

[
{
"start": 20,
"end": 50
},
{
"start": 50,
"end": 80
}
]

## Week 1 Deliverables

* Transcript processing
* Scoring logic
* Ranking system
* Non-overlapping clip filtering
* Output generation
* Project documentation
