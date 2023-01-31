SESSION_CONFIGS = [
    dict(
        name="flow_market",
        display_name="Flow Market",
        num_demo_participants=6,
        app_sequence=["flow_market"],
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

ROOMS = [
    dict(name='live_demo', 
        display_name='Room for live demo (no participant labels)'
    ),
    dict(
        name='sequential_search',
        display_name='Sequential Search',
        participant_label_file='_rooms/participant_label.txt',
        # use_secure_urls=True
    ),
    dict(
        name='leeps',
        display_name='LEEPS',
        participant_label_file='_rooms/participant_label.txt',
        # use_secure_urls=True
    ),
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = "1234"

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "vie)38p_nw-tz!y-6^ewrvq_^eai$@a3l3iv*fdqe5b$p!%1jw"

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ["otree"]
