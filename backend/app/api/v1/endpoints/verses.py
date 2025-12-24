from fastapi import APIRouter
import random

router = APIRouter()

# Curated verses for each mood category
MOOD_VERSES = {
    "happy": [
        {
            "verse": "This is the day that the Lord has made; let us rejoice and be glad in it.",
            "reference": "Psalm 118:24",
            "devotional": "Your joy today is a gift from God. Let it overflow and bless those around you!"
        },
        {
            "verse": "Rejoice in the Lord always; again I will say, rejoice!",
            "reference": "Philippians 4:4",
            "devotional": "Your happiness is contagious. Share the joy God has given you with others today."
        },
        {
            "verse": "The joy of the Lord is your strength.",
            "reference": "Nehemiah 8:10",
            "devotional": "Let this joy fuel your day. God celebrates with you in your happiness!"
        }
    ],
    "sad": [
        {
            "verse": "The Lord is close to the brokenhearted and saves those who are crushed in spirit.",
            "reference": "Psalm 34:18",
            "devotional": "God sees your tears and He's right there with you. You're not alone in this moment."
        },
        {
            "verse": "Come to me, all who are weary and burdened, and I will give you rest.",
            "reference": "Matthew 11:28",
            "devotional": "It's okay to not be okay. Bring your sadness to God - He can handle it all."
        },
        {
            "verse": "Weeping may stay for the night, but rejoicing comes in the morning.",
            "reference": "Psalm 30:5",
            "devotional": "This feeling won't last forever. Brighter days are ahead, even if you can't see them yet."
        }
    ],
    "anxious": [
        {
            "verse": "Do not be anxious about anything, but in everything by prayer present your requests to God.",
            "reference": "Philippians 4:6",
            "devotional": "Take a breath. God wants to hear what's worrying you. Talk to Him about it."
        },
        {
            "verse": "Cast all your anxiety on Him because He cares for you.",
            "reference": "1 Peter 5:7",
            "devotional": "You don't have to carry this alone. God is ready to take this burden from you."
        },
        {
            "verse": "When anxiety was great within me, your consolation brought me joy.",
            "reference": "Psalm 94:19",
            "devotional": "Even in the midst of worry, God's peace is available to you right now."
        }
    ],
    "angry": [
        {
            "verse": "In your anger do not sin. Do not let the sun go down while you are still angry.",
            "reference": "Ephesians 4:26",
            "devotional": "It's okay to feel angry, but don't let it control you. God can help you process this."
        },
        {
            "verse": "A gentle answer turns away wrath, but a harsh word stirs up anger.",
            "reference": "Proverbs 15:1",
            "devotional": "Take a moment before responding. God can give you wisdom in how to handle this."
        },
        {
            "verse": "Be slow to speak and slow to become angry, for human anger does not produce righteousness.",
            "reference": "James 1:19-20",
            "devotional": "Your feelings are valid. Let God help you channel this energy in a healthy way."
        }
    ],
    "stressed": [
        {
            "verse": "Peace I leave with you; my peace I give you. Not as the world gives do I give to you.",
            "reference": "John 14:27",
            "devotional": "In the middle of chaos, God's peace is still available. Take a moment to breathe it in."
        },
        {
            "verse": "God is our refuge and strength, an ever-present help in trouble.",
            "reference": "Psalm 46:1",
            "devotional": "You don't have to figure everything out right now. God's got this with you."
        },
        {
            "verse": "My grace is sufficient for you, for my power is made perfect in weakness.",
            "reference": "2 Corinthians 12:9",
            "devotional": "It's okay to feel overwhelmed. God's strength shows up when you feel weakest."
        }
    ],
    "grateful": [
        {
            "verse": "Give thanks to the Lord, for He is good; His love endures forever.",
            "reference": "Psalm 107:1",
            "devotional": "Your gratitude honors God. Keep noticing His goodness in your life today."
        },
        {
            "verse": "In everything give thanks, for this is God's will for you in Christ Jesus.",
            "reference": "1 Thessalonians 5:18",
            "devotional": "Gratitude shifts everything. You're cultivating a beautiful perspective today!"
        },
        {
            "verse": "Let them give thanks to the Lord for His unfailing love and His wonderful deeds.",
            "reference": "Psalm 107:8",
            "devotional": "Count your blessings one by one. God loves when His children notice His gifts."
        }
    ],
    "peaceful": [
        {
            "verse": "You will keep in perfect peace those whose minds are steadfast, because they trust in you.",
            "reference": "Isaiah 26:3",
            "devotional": "Rest in this peace. It's a gift from God. Soak it in and carry it with you."
        },
        {
            "verse": "Let the peace of Christ rule in your hearts, to which indeed you were called.",
            "reference": "Colossians 3:15",
            "devotional": "This calm you feel is sacred. Let it anchor you throughout your day."
        },
        {
            "verse": "The Lord gives strength to His people; the Lord blesses His people with peace.",
            "reference": "Psalm 29:11",
            "devotional": "Peace is yours today. God is with you in this beautiful, calm moment."
        }
    ],
    "lonely": [
        {
            "verse": "The Lord himself goes before you and will be with you; He will never leave you.",
            "reference": "Deuteronomy 31:8",
            "devotional": "You're not alone, even when it feels like it. God is right here with you."
        },
        {
            "verse": "God sets the lonely in families and leads forth the prisoners with singing.",
            "reference": "Psalm 68:6",
            "devotional": "God sees your loneliness and He cares. He's working to bring connection into your life."
        },
        {
            "verse": "I am with you always, even to the end of the age.",
            "reference": "Matthew 28:20",
            "devotional": "Even in solitude, God's presence surrounds you. You are deeply loved and never forgotten."
        }
    ],
    "default": [
        {
            "verse": "I can do all things through Christ who strengthens me.",
            "reference": "Philippians 4:13",
            "devotional": "Whatever today brings, you have God's strength available to you. You've got this!"
        },
        {
            "verse": "Trust in the Lord with all your heart and lean not on your own understanding.",
            "reference": "Proverbs 3:5",
            "devotional": "You don't have to have it all figured out. Trust God with today's journey."
        },
        {
            "verse": "For I know the plans I have for you, declares the Lord, plans to prosper you.",
            "reference": "Jeremiah 29:11",
            "devotional": "God has good plans for you. Keep moving forward with hope and trust."
        }
    ]
}


@router.get("/daily-verse")
async def get_daily_verse(mood: str = "default"):
    """
    Get a scripture verse and devotional based on the user's mood.
    Returns a random verse from the appropriate mood category.
    """
    # Normalize mood to lowercase and get verses
    mood_key = mood.lower()
    
    # If mood not in our categories, use default
    if mood_key not in MOOD_VERSES:
        mood_key = "default"
    
    verses = MOOD_VERSES[mood_key]
    selected_verse = random.choice(verses)
    
    return {
        "mood": mood_key,
        "verse": selected_verse["verse"],
        "reference": selected_verse["reference"],
        "devotional": selected_verse["devotional"]
    }
