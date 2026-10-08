# 장면별 내레이션(문장 단위로 TTS)과 화면 큐.
# cue: (이름, 문장 index, 기준 구절) — 구절이 None이면 문장 시작, "END"면 문장 끝.
# 구절 위치는 문장 안 글자 비율로 시간을 추정한다.

SCENES = [
    {"id": "intro", "sentences": [
        "This video introduces the improvement plan for JEI Math Grades D through I.",
        "We will explore the three key directions for improvement, the detailed changes for each grade, and how the supplementary materials will be utilized.",
     ], "cues": [
        ("agenda1", 1, "three key"),
        ("agenda2", 1, "the detailed"),
        ("agenda3", 1, "and how"),
     ]},
    {"id": "priority", "sentences": [
        "Currently, approximately 80 percent of our total members are concentrated in Grades D through I.",
        "Therefore, based on JEI's unique and systematic learning structure, we have selected these grades as our top priority for improvement, with the goal of strengthening alignment with the Common Core State Standards, CCSS, and optimizing the learner experience.",
     ], "cues": [
        ("highlight", 0, "80 percent"),
        ("shift", 1, None),
        ("prio1", 1, "strengthening alignment"),
        ("prio2", 1, "optimizing"),
     ]},
    {"id": "roadmap", "sentences": [
        "The first area of improvement is to strengthen the incorporation of the CCSS.",
        "When comparing JEI's learning sequence with the CCSS progression, the timing and progression of learning do not always align.",
        "In particular, we will closely review the timing and progression of learning and CCSS alignment.",
     ], "cues": [
        ("roadmapLabel", 1, None),
        ("chevrons", 1, "the timing"),
     ]},
    {"id": "align", "sentences": [
        "Building on JEI's systematic learning roadmap, we aim to further enhance alignment with grade-level standards in the U.S., maximizing both the timeliness and completeness of learning.",
     ], "cues": [
        ("jeiTrack", 0, None),
        ("ccssTrack", 0, "further enhance"),
        ("addContent", 0, "grade-level"),
        ("bottom", 0, "maximizing"),
     ]},
    {"id": "gradeD", "sentences": [
        "For example, in Grade D, we have strengthened students' understanding of the relational meaning of the equal sign, emphasizing that both sides represent equal quantities.",
        "We have also added word problems involving three numbers to further develop students' ability to apply mathematical concepts to real-life situations.",
     ], "cues": [
        ("eq", 0, "relational meaning"),
        ("eqTrue", 0, "both sides"),
        ("wp", 1, None),
        ("rabbits", 1, "three numbers"),
        ("sum", 1, "to apply"),
     ]},
    {"id": "gradeI", "sentences": [
        "In Grade I, we have newly introduced the coordinate plane and strengthened learning related to comparing integers and understanding absolute value, allowing students to progress naturally toward more advanced concepts.",
     ], "cues": [
        ("plane", 0, "newly introduced"),
        ("integers", 0, "strengthened learning"),
        ("abs", 0, "understanding absolute"),
     ]},
    {"id": "synergy", "sentences": [
        "Through these changes, we will connect JEI's strong learning system more closely with the local curriculum and further strengthen the natural connections between concepts across grades.",
     ], "cues": [
        ("s1", 0, "JEI's strong"),
        ("s2", 0, "the local curriculum"),
        ("s3", 0, "further strengthen"),
        ("result", 0, "natural connections"),
     ], "tail": 1.6},
    {"id": "workbook", "sentences": [
        "The second direction is to improve page structure based on the amount of learning content.",
        "The existing pages provided 12 to 24 calculation practice problems, offering students valuable opportunities for practice and mastery.",
        "However, to reduce learner fatigue and help students focus more deeply on concepts, we have reorganized the content more efficiently.",
        "Accordingly, the main textbook has been redesigned around conceptual understanding and representative problems, allowing students to focus on key learning objectives while providing sufficient space for solving problems.",
     ], "cues": [
        ("current", 1, None),
        ("currentNote", 1, "offering"),
        ("reorg", 2, "we have reorganized"),
        ("b1", 3, "conceptual understanding"),
        ("b2", 3, "focus on key"),
        ("b3", 3, "sufficient space"),
        ("fatigue", 3, "END"),
     ], "tail": 2.2},
    {"id": "supp", "sentences": [
        "The repetitive practice problems reduced from the main textbook will be reorganized into supplementary materials, customized for each set.",
        "When students need additional practice after completing the main textbook, centers will be able to download, print, and provide the appropriate materials.",
     ], "cues": [
        ("f1", 0, None),
        ("f2", 0, "reorganized into"),
        ("f3", 1, "additional practice"),
        ("box", 1, "centers"),
        ("dl", 1, "download"),
        ("pr", 1, "print,"),
        ("pv", 1, "provide"),
     ]},
    {"id": "mastery", "sentences": [
        "This approach reduces unnecessary learning burden in the main textbook while still providing sufficient opportunities for mastery through supplementary materials directly connected to each target set, ultimately supporting mastery learning.",
     ], "cues": [
        ("core", 0, None),
        ("supp", 0, "while still"),
        ("master", 0, "ultimately"),
     ]},
    {"id": "sequence", "sentences": [
        "The third direction is to strengthen the connection between prerequisite concepts and subsequent learning.",
        "Building on JEI's strong conceptual structure, we have further subdivided the learning steps so that students can transition more easily to higher-level concepts such as equations, fractions, and decimals.",
     ], "cues": [
        ("left", 1, None),
        ("right", 1, "further subdivided"),
        ("rightNote", 1, "transition"),
     ]},
    {"id": "gradeF", "sentences": [
        "In Grade F, we have designed the concept of equal partitioning to naturally lead into fraction notation.",
        "We have also introduced the use of variables progressively according to students' grade levels to support intuitive understanding of equations.",
     ], "cues": [
        ("partition", 0, "equal partitioning"),
        ("fraction", 0, "fraction notation"),
        ("vars", 1, None),
        ("equations", 1, "intuitive"),
     ]},
    {"id": "gradeGH", "sentences": [
        "In Grades G and H, we have strengthened the use of visual models, such as number lines, area models, and grouping models, so that students can develop a more intuitive understanding of rounding and the principles of multiplying and dividing fractions.",
     ], "cues": [
        ("m1", 0, "number lines"),
        ("m2", 0, "area models"),
        ("m3", 0, "grouping models"),
        ("caption", 0, "intuitive"),
     ]},
    {"id": "gradeI2", "sentences": [
        "Furthermore, in Grade I, these foundations are systematically extended so that relationships between two variables naturally progress from equations to tables and then to graphs.",
     ], "cues": [
        ("equ", 0, "relationships"),
        ("tab", 0, "to tables"),
        ("gra", 0, "to graphs"),
        ("caption", 0, "END"),
     ], "tail": 2.0},
    {"id": "cycle", "sentences": [
        "Along with the evolution of these learning objectives, we are also redesigning the diagnostic assessment and system data.",
        "Based on the revised standards, the system will not only accurately identify each student's starting point but also automatically connect the results to personalized supplementary-material recommendations.",
        "This will create a more complete learning cycle from diagnosis to prescription to learning.",
     ], "cues": [
        ("sys", 0, "diagnostic"),
        ("diag", 1, "accurately"),
        ("presc", 1, "automatically"),
        ("learn", 2, None),
        ("loop", 2, "from diagnosis"),
     ]},
    {"id": "scope", "sentences": [
        "Through these improvements, 140 of the 221 existing sets will maintain their current structure, while 81 sets will be revised and enhanced and 5 new sets will be added.",
     ], "cues": [
        ("n140", 0, "140"),
        ("n221", 0, "221"),
        ("n81", 0, "81 sets"),
        ("n5", 0, "5 new"),
        ("n226", 0, "END"),
     ], "tail": 3.2},
    {"id": "package", "sentences": [
        "For each grade, we will comprehensively implement the main textbook revision, system data updates, and supplementary-material development as one integrated package.",
     ], "cues": [
        ("p1", 0, "main textbook"),
        ("p2", 0, "system data"),
        ("p3", 0, "supplementary"),
        ("unit", 0, "one integrated"),
     ], "tail": 1.6},
    {"id": "outro", "sentences": [
        "Through this improvement aligned with global standards, we aim to help students understand mathematical concepts more clearly and confidently extend their learning to the next level.",
        "Thank you.",
     ], "cues": [
        ("lead", 0, "we aim"),
        ("o1", 0, "understand"),
        ("o2", 0, "confidently"),
        ("thanks", 1, None),
     ], "tail": 2.5},
]
