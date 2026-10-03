"""Security-awareness guidance (static educational content)."""

LEVEL_GUIDANCE = {
    "LOW": "Good habits overall. Keep reviewing settings every few months and stay alert to scams.",
    "MODERATE": "A few gaps. Fix the highest-priority items first; most take under 10 minutes.",
    "HIGH": "Significant exposure. Start with MFA, unique passwords and audience settings this week.",
    "CRITICAL": "Very high exposure. Secure login (MFA, unique passwords) today, then reduce public visibility.",
}

TIPS = [
    ("Turn on MFA everywhere",
     "An authenticator app or security key blocks most password-only takeovers."),
    ("Use a password manager",
     "It creates and stores a unique password per site so one breach stays contained."),
    ("Share less, later",
     "Post trips after you return and avoid live location; routines make scams believable."),
    ("Limit your audience",
     "Friends-only defaults and manual follower approval cut off most strangers."),
    ("Audit apps and sessions",
     "Remove unused connected apps and unknown logged-in devices regularly."),
    ("Pause and verify",
     "Urgent requests for money, codes or logins are verified through a second channel."),
]

RED_FLAGS = [
    "Urgent wording: 'account locked', 'act now', 'you won'.",
    "A friend's 'new account' asking for money, codes or favours.",
    "Links that don't match the official domain or use shortened URLs.",
    "Requests for verification codes, passwords or gift cards.",
    "Profiles with few posts, stock photos, or many sudden follow requests.",
]
