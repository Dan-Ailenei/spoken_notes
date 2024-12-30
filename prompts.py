def get_prompt1(input: str):
    return f"""
A transcript is provided below of a voice memo I recorded as a "note to self". please extract all the points made or thoughts described, and put them in bullet-point form. use nested bullet points to indicate structure, e.g. a top-level bullet for each topic area and sub-bullets underneath. use multi-level nesting as appropriate to organize the thinking logically. use markdown formatting with `- [ ] ` to create tasks instead of `-`  to create tasks for bullet points.

DO NOT OMIT ANY POINTS MADE. This is not a summarization task — your only goal is to structure the thoughts there so they are logically organized and easy to read. Be concise because the reader is busy, but again DO NOT omit any points made.

Every bullet point should be after a topic title, specified on its own line with no styling, using sentence casing. For example:

This instructions are in english but the text will be in Romanian.
```
Topic 1
- [ ] Bullet point 1
- [ ] Bullet point 2

Topic 2
- [ ] Bullet point n
...
```

Make sure topic titles are substantive, such as "Work" or "Time with friends", NOT catch-alls like "Future plans and considerations".

Minimize the number of bullet points you need to do your job. Also, only create additional levels of nesting when needed. NEVER have a bullet point with only one nested sub-bullet point — just fit the information on the parent's nesting level instead, EXCEPT if it's a single nested bullet point underneath a top-level topic bullet point.

Write the summary from the first person, e.g. you can say "I". Do not use sentence fragments, e.g. omitting subjects or auxiliary verbs. Prefer full sentences, although ONLY use punctuation when there will be more than one sentence on the line or if it's a question mark or exclamation mark. If there is only one sentence or sentence fragment on a line, DO NOT end it with a period; just leave no punctuation on the end unless it's a question.

Group similar topics together, so that if the transcript jumps around, thoughts are still organized so they flow contiguously and do not jump around. For example, if the transcript discusses couple's therapy, then work, then the relationship, organize your output to discuss couple's therapy, then the relationship, then work.

Ignore any bracketed sound descriptions, e.g. "[chewing]".

Ignore introductory or concluding remarks that don't have substantive content, e.g. "Daily log", "Good morning", "Good night", "Going to bed now", etc.

Rewrite awkward language to use simple words that flow naturally, for example instead of "My sleep radar confirmed the short sleep duration", use more readable language such as "My sleep radar confirmed I didn't sleep much last night".

Use numerals rather than writing out number, for example instead of "four and a half hours", say "4.5 hours", EXCEPT when the number is three or less and referring to a quantity that is typically three or less, such as "two peas in a pod" or "loved one".

Here are some examples of bad patterns and how they can be improved:


## Example 1: 
Bad:
```
- [ ] Daily log
  - [ ] Today was a good day
    - [ ] Felt somewhat productive
```
Better:
```
- [ ] Today was a productive and good day
```

The second version keeps all information, uses only one bullet point, and only one level of nesting.


## Example 2
Bad:
```
- [ ] Lawyer call
  - [ ] Spoke with a corporate lawyer
    - [ ] Very useful
    - [ ] Consider talking to another person for corroboration
  - [ ] Legal insights
    - [ ] (...)
```
Better:
```
- [ ] Call with corporate lawyer
  - [ ] Useful
  - [ ] Consider talking to another lawyer to validate what we learned
  - [ ] (...)
```
Here's why this one is better:
* Combined the first two lines without any loss in information, and removed a level of indentation that wasn't needed
* Changed "Very useful" to just "Useful" for simplicity — note when speaking filler words or words like "very"/etc aren't needed when reading in written form to still get the idea
* Replaced "another person" with "another lawyer" to be more specific without making the text longer
* "validate what we learned", even though it's longer than "corroboration", is still better because we should avoid complicated words, e.g. those with five or more syllables, or are esoteric
* Removed the "Legal insights" bullet point, saving one bullet *and* saving an extra level of nesting, without loss of meaning — any insights can fit under the "Call with corporate lawyer" bullet point just fine


## Example 3
Bad:
```
  - [ ] Mentioned to Jackie willingness to help for six months
    - [ ] Bob pre-approved this idea
```
Better:
```
  - [ ] I told Jackie I'm willing to help for six months. Bob pre-approved this idea.
  - [ ] (...)
```
This is better because it avoid indentation where there is only one sub-bullet. It also avoids informal ellipsis.


## Example 4
Bad:
```
- [ ] Work productivity
  - [ ] Wrote a small amount of code.
  - [ ] Felt less inclined to write code after Bob went to bed.
```
Better:
```
- [ ] Work productivity
  - [ ] I wrote a small amount of code
  - [ ] I didn't feel like writing code after Bob went to bed
```
This is better because (1) it does not put periods at the end of sentences when they are not needed to separate multiple sentences on one line, (2) It uses full sentences, avoiding ellipses / sentence fragments, (2) The last bullet point is rewritten to use active voice (better), and avoided an ambiguous "less inclined" (less inclined than what?).


## Example 5
Bad:
```
  - [ ] (...)
  - [ ] Couples therapy is scheduled for tomorrow.
    - [ ] Uncertain about what to work on in the session.
  - [ ] (...)
```
Better:
```
  - [ ] (...)
  - [ ] Our couples therapy is scheduled for tomorrow. I don't know what to work on in the session.
  - [ ] (...)
```
This is better because it avoids sentence fragments, and avoids indentation levels with only one bullet point.

# Your input: the transcript to work on
```
{input}
```
"""


def get_prompt2(input: str):
    return f"""
# Instructions
These sections and bullet points are from a single note to self. Please rewrite them so the text flows logically, while preserving all the information.

## Reordering sections

Sections should be ordered so they flow logically.

### Minimizing topic jumps

For example, if sections are "My relationship", "Work", and then "Family", then it would flow better to put them in the order "My relationship", "Family", then "Work". By "flow better" this means that the total deltas between each topic jump is minimized.

### Order by me → the world

Where bullet points exist relating to each of these things. start with sections related to me alone, for example my sleep, my health. Then expand to anything related to my relationship with ___. Then expand to anything related to my family. Then expand to anything related to my social life. Then expand to anything related to my work. Then expand to anything related to the broad world.

Do NOT force sections to be there when there isn't content directly related to the topic.

There may be limited exceptions to this if there is VERY important information to put first, for example if the first thing in the input is about me e.g. being fired at work, then that should go first because everything else (e.g. updates about my family) will probably depend on that context of being fired. But otherwise use the ordering of me → broad world.


## Combining sections

Please combine sections that are very similar in topic. Here are some examples:

- [ ] These topics are all distinct enough they should NOT be combined any further: Sleep and health, Relationship, Family, Work, Social / friends.
- [ ] These topics are NOT distinct enough to warrant their own sections and should all be combined: "Work on AI Notes", "AI Notes development", "Project integration and future plans" (where the bullets under the last title relate to the 'AI Notes' project)

It may be helpful to know that ___, ___, and ___ (sometimes misspelled "___") are my immediate family.

When combining sections, make sure the bullet points flow in a logical order as well so they make sense and flow easily from one to the next.

Rewrite the combined section title so it is concise yet descriptive, for example if combining sections with titles "Work on AI Notes" and "AI Notes development", a good combined title would be "Work on AI Notes". AVOID compound titles ("X and Y") where it would be sufficiently descriptive to only have one noun phrase, for example:

- [ ] Instead of "Distractions and focus", just write "Distractions"
- [ ] Instead of "Social interactions and activities", just write "Social"

Section titles should be sentence cased, for example "Sleep and health".

There should only be one newline character between the end of a title and the first bullet point, for example:

```
Title 1
- [ ] Bullet point
```


## Combining bullet points

If two bullet points can be combined without a loss in information, combine them. When editing bullet points' text, follow these rules for punctuation: Prefer full sentences, although ONLY use punctuation when there will be more than one sentence on the line or if it's a question mark or exclamation mark. If there is only one sentence or sentence fragment on a line, DO NOT end it with a period; just leave no punctuation on the end unless it's a question.

# Your input: the transcript to work on
```
{input}
```"""
