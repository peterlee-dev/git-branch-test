# 장면별 내레이션(TTS 한 파일을 문장 단위로 잘라 씀)과 화면 큐.
# 문장: 자막·화면에 쓰는 바른 문장(대본 PDF 그대로). " | " 는 자막을 나누는 자리(음성은 한 덩어리로 자름)
# cue: (이름, 문장 index, 기준 구절) — 구절이 None이면 문장 시작, "END"면 문장 끝.
# 구절 시각은 받아쓰기 단어 타임스탬프(source/di_tts_words.json)에서 그 구절 첫 단어가 시작하는 때.

SCENES = [
    {"id": "intro", "sentences": [
        "This video introduces the improvement plan for JEI Math Grades D–I.",
        "We will explore the three key directions for improvement, the detailed changes for each grade, | and how the supplementary materials will be utilized.",
     ], "cues": [
        ("agenda1", 1, "three key"),
        ("agenda2", 1, "the detailed"),
        ("agenda3", 1, "how the supplementary"),
     ]},
    {"id": "priority", "sentences": [
        "Currently, approximately 80% of our total members are concentrated in Grades D–I.",
        "Therefore, based on JEI’s unique and systematic learning structure, | we have selected these grades as our top priority for improvement, | with the goal of strengthening alignment with the Common Core State Standards (CCSS) | and optimizing the learner experience.",
     ], "cues": [
        ("highlight", 0, "80%"),
        ("shift", 1, None),
        ("base", 1, "based on"),
        ("prio1", 1, "strengthening alignment"),
        ("prio2", 1, "optimizing"),
     ]},
    {"id": "roadmap", "sentences": [
        "The first area of improvement is to strengthen the incorporation of the CCSS.",
        "When comparing JEI’s learning sequence with the CCSS progression, | the timing and progression of learning do not always align.",
        "In particular, we will closely review the timing and progression of learning and CCSS alignment.",
     ], "cues": [
        ("steps", 1, "JEI’s learning"),
        ("review", 2, "closely review"),
        ("tp", 2, "the timing"),
        ("align", 2, "CCSS alignment"),
     ]},
    {"id": "standards", "sentences": [
        "Building on JEI’s systematic learning roadmap, | we aim to further enhance alignment with grade-level standards in the U.S., | maximizing both the timeliness and completeness of learning.",
     ], "cues": [
        ("road", 0, None),
        ("enh", 0, "further enhance"),
        ("std", 0, "grade-level standards"),
        ("max", 0, "maximizing"),
        ("time", 0, "timeliness"),
        ("comp", 0, "completeness"),
     ]},
    {"id": "gradeD", "sentences": [
        "For example, in Grade D, we have strengthened students’ understanding of the relational meaning of the equal sign, | emphasizing that both sides represent equal quantities.",
        "We have also added word problems involving three numbers | to further develop students’ ability to apply mathematical concepts to real-life situations.",
     ], "cues": [
        ("eq", 0, "relational meaning"),
        ("eqTrue", 0, "both sides"),
        ("wp", 1, None),
        ("rabbits", 1, "involving"),
        ("add", 1, "three numbers"),
        ("sub", 1, "to further"),
        ("sum", 1, "apply"),
     ]},
    {"id": "gradeI", "sentences": [
        "In Grade I, we have newly introduced the coordinate plane | and strengthened learning related to comparing integers and understanding absolute value, | allowing students to progress naturally toward more advanced concepts.",
     ], "cues": [
        ("plane", 0, "newly introduced"),
        ("integers", 0, "comparing integers"),
        ("abs", 0, "absolute value"),
        ("adv", 0, "progress naturally"),
     ]},
    {"id": "synergy", "sentences": [
        "Through these changes, we will connect JEI’s strong learning system more closely with the local curriculum | and further strengthen the natural connections between concepts across grades.",
     ], "cues": [
        ("s1", 0, "JEI’s strong"),
        ("s2", 0, "local curriculum"),
        ("conv", 0, "and further"),
        ("prog", 0, "the natural"),
        ("levels", 0, "between concepts"),
        ("result", 0, "across grades"),
     ], "tail": 1.6},
    {"id": "workbook", "sentences": [
        "The second direction is to improve page structure based on the amount of learning content.",
        "The existing pages provided 12 to 24 calculation practice problems, | offering students valuable opportunities for practice and mastery.",
        "However, to reduce learner fatigue and help students focus more deeply on concepts, | we have reorganized the content more efficiently.",
        "Accordingly, the main textbook has been redesigned around conceptual understanding and representative problems, | allowing students to focus on key learning objectives | while providing sufficient space for solving problems.",
     ], "cues": [
        ("current", 1, None),
        ("count", 1, "12 to 24"),
        ("currentNote", 1, "valuable"),
        ("focus", 2, "reduce learner"),
        ("strike", 2, "reorganized"),
        ("reorg", 3, "main textbook"),
        ("b1", 3, "conceptual understanding"),
        ("b3", 3, "focus on key"),
        ("b2", 3, "sufficient space"),
        ("fatigue", 3, "END"),
     ], "tail": 1.8},
    {"id": "supp", "sentences": [
        "The repetitive practice problems reduced from the main textbook | will be reorganized into supplementary materials customized for each set.",
        "When students need additional practice after completing the main textbook, | centers will be able to use these materials flexibly according to individual learning needs.",
     ], "cues": [
        ("f1", 0, None),
        ("f2", 0, "reorganized into"),
        ("f3", 1, "additional practice"),
        ("box", 1, "centers"),
        ("flex", 1, "flexibly"),
        ("needs", 1, "individual"),
     ]},
    {"id": "mastery", "sentences": [
        "This approach reduces unnecessary learning burden in the main textbook | while still providing sufficient opportunities for mastery | through supplementary materials directly connected to each target set, | ultimately supporting mastery learning.",
     ], "cues": [
        ("core", 0, "reduces unnecessary"),
        ("supp", 0, "while still"),
        ("linked", 0, "directly connected"),
        ("master", 0, "ultimately"),
     ]},
    {"id": "sequence", "sentences": [
        "The third direction is to strengthen the connection between prerequisite concepts and subsequent learning.",
        "Building on JEI’s strong conceptual structure, we have further subdivided the learning steps | so that students can transition more easily to higher-level concepts | such as equations, fractions, and decimals.",
     ], "cues": [
        ("left", 1, None),
        ("right", 1, "further subdivided"),
        ("flow", 1, "transition"),
        ("higher", 1, "higher-level"),
        ("c1", 1, "equations"),
        ("c2", 1, "fractions"),
        ("c3", 1, "decimals"),
     ]},
    {"id": "gradeF", "sentences": [
        "In Grade F, we have designed the concept of equal partitioning to naturally lead into fraction notation.",
        "We have also introduced the use of variables progressively according to students’ grade levels | to support intuitive understanding of equations.",
     ], "cues": [
        ("partition", 0, "equal partitioning"),
        ("fraction", 0, "fraction notation"),
        ("vars", 1, "use of variables"),
        ("prog", 1, "progressively"),
        ("grade", 1, "grade levels"),
        ("equations", 1, "intuitive"),
     ]},
    {"id": "gradeGH", "sentences": [
        "In Grades G and H, we have strengthened the use of visual models, | such as number lines, area models, and grouping models, | so that students can develop a more intuitive understanding of rounding | and the principles of multiplying and dividing fractions.",
     ], "cues": [
        ("models", 0, "visual models"),
        ("m1", 0, "number lines"),
        ("m2", 0, "area models"),
        ("m3", 0, "grouping models"),
        ("caption", 0, "intuitive"),
     ]},
    {"id": "gradeI2", "sentences": [
        "Furthermore, in Grade I, these foundations are systematically extended | so that relationships between two variables naturally progress from equations to tables and then to graphs.",
     ], "cues": [
        ("equ", 0, "relationships"),
        ("tab", 0, "to tables"),
        ("gra", 0, "to graphs"),
        ("caption", 0, "END"),
     ], "tail": 1.6},
    {"id": "cycle", "sentences": [
        "Along with the evolution of these learning objectives, | we are also redesigning the diagnostic assessment and system data.",
        "Based on the revised standards, the system will not only accurately identify each student’s starting point | but also automatically connect the results to personalized supplementary-material recommendations.",
        "This will create a more complete learning cycle from diagnosis to prescription to learning.",
     ], "cues": [
        ("sys", 0, "redesigning"),
        ("obj", 1, None),
        ("diag", 1, "accurately identify"),
        ("presc", 1, "automatically connect"),
        ("cyc", 2, "a more complete"),
        ("learn", 2, "to learning"),
     ], "tail": 1.4},
    {"id": "scope", "sentences": [
        "Through these improvements, 140 of the 221 existing sets will maintain their current structure, | while 81 sets will be revised and enhanced and 5 new sets will be added.",
     ], "cues": [
        ("n140", 0, "140"),
        ("n221", 0, "221"),
        ("n81", 0, "81"),
        ("n5", 0, "5 new"),
     ], "tail": 1.8},
    {"id": "package", "sentences": [
        "For each grade, we will comprehensively implement the main textbook revision, system data updates, | and supplementary-material development as one integrated package.",
     ], "cues": [
        ("p1", 0, "main textbook"),
        ("p2", 0, "system data"),
        ("p3", 0, "supplementary-material"),
        ("unit", 0, "as one"),
     ], "tail": 1.4},
    {"id": "outro", "sentences": [
        "Through this improvement aligned with global standards, | we aim to help students understand mathematical concepts more clearly | and confidently extend their learning to the next level.",
        "Thank you.",
     ], "cues": [
        ("lead", 0, None),
        ("o1", 0, "understand mathematical"),
        ("o2", 0, "confidently"),
        ("thanks", 1, None),
     ], "tail": 2.5},
]
