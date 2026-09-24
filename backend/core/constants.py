"""
Domain constants for the AI Car Mechanic application.
Centralized configuration for validation, domain filtering, and choices.
"""

# --- Automotive domain keywords for deterministic filtering ---
# Used to check if a user message is car-related before calling Gemini.
CAR_KEYWORDS = {
    # Vehicle types
    'car', 'truck', 'suv', 'van', 'sedan', 'coupe', 'hatchback', 'convertible',
    'minivan', 'pickup', 'vehicle', 'automobile', 'auto', 'motorcycle', 'bike',
    # Parts
    'engine', 'motor', 'transmission', 'brake', 'brakes', 'clutch', 'gear',
    'gearbox', 'tire', 'tyre', 'wheel', 'axle', 'suspension', 'shock',
    'strut', 'spring', 'steering', 'radiator', 'coolant', 'thermostat',
    'alternator', 'starter', 'battery', 'spark', 'plug', 'ignition',
    'exhaust', 'muffler', 'catalytic', 'converter', 'turbo', 'supercharger',
    'carburetor', 'injector', 'fuel', 'gasoline', 'diesel', 'petrol', 'gas',
    'oil', 'filter', 'air', 'cabin', 'belt', 'timing', 'serpentine', 'chain',
    'piston', 'cylinder', 'crankshaft', 'camshaft', 'valve', 'gasket',
    'head', 'manifold', 'intake', 'throttle', 'sensor', 'oxygen', 'o2',
    'abs', 'airbag', 'seatbelt', 'windshield', 'wiper', 'headlight',
    'taillight', 'bumper', 'fender', 'hood', 'trunk', 'door', 'window',
    'mirror', 'dashboard', 'speedometer', 'tachometer', 'odometer',
    'gauge', 'ac', 'heater', 'compressor', 'condenser', 'evaporator',
    'hose', 'clamp', 'bolt', 'nut', 'bearing', 'bushing', 'joint', 'cv',
    'driveshaft', 'differential', 'transfer', 'flywheel', 'torque',
    'caliper', 'rotor', 'pad', 'drum', 'shoe', 'master', 'slave',
    'power', 'pump', 'water', 'fuel', 'relay', 'fuse', 'wiring',
    'ecu', 'pcm', 'obd', 'diagnostic', 'scanner', 'code',
    # Symptoms
    'noise', 'sound', 'vibration', 'shake', 'shaking', 'wobble',
    'squeal', 'squeak', 'grinding', 'clicking', 'clunking', 'knocking',
    'rattling', 'humming', 'whining', 'hissing', 'popping', 'ticking',
    'leak', 'leaking', 'drip', 'dripping', 'smoke', 'smoking',
    'overheat', 'overheating', 'stall', 'stalling', 'misfire',
    'rough', 'idle', 'idling', 'hesitation', 'surge', 'surging',
    'pull', 'pulling', 'drift', 'drifting', 'vibrate', 'shimmy',
    'dead', 'wont', "won't", 'start', 'starting', 'crank', 'cranking',
    'turn', 'over', 'acceleration', 'accelerate', 'decelerate',
    'slow', 'sluggish', 'jerking', 'jerk', 'buck', 'bucking',
    'smell', 'odor', 'burning', 'sweet', 'rotten', 'sulfur',
    'warning', 'light', 'check', 'indicator', 'lamp', 'flash',
    'flashing', 'blinking', 'dim', 'bright', 'flicker',
    # Actions
    'drive', 'driving', 'park', 'parking', 'reverse', 'reversing',
    'shift', 'shifting', 'accelerating', 'braking', 'turning',
    'steering', 'stopping', 'idling', 'starting', 'cranking',
    'tow', 'towing', 'jump', 'jumpstart',
    # Maintenance
    'repair', 'fix', 'replace', 'install', 'remove', 'change',
    'flush', 'bleed', 'align', 'alignment', 'balance', 'rotate',
    'rotation', 'tune', 'tuneup', 'service', 'maintenance',
    'inspection', 'inspect', 'diagnose', 'troubleshoot', 'mechanic',
    'garage', 'shop', 'dealer', 'dealership', 'warranty',
    'mileage', 'odometer', 'mpg', 'kilometer', 'mile',
    # Brands (common)
    'honda', 'toyota', 'ford', 'chevy', 'chevrolet', 'nissan',
    'hyundai', 'kia', 'bmw', 'mercedes', 'benz', 'audi',
    'volkswagen', 'vw', 'subaru', 'mazda', 'lexus', 'acura',
    'infiniti', 'volvo', 'jeep', 'dodge', 'ram', 'chrysler',
    'buick', 'cadillac', 'gmc', 'lincoln', 'tesla', 'porsche',
    'jaguar', 'rover', 'fiat', 'alfa', 'mitsubishi', 'suzuki',
    'peugeot', 'renault', 'citroen', 'skoda', 'seat', 'tata',
    'mahindra', 'maruti',
}

# --- File upload validation ---
ALLOWED_IMAGE_MIMES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
}

ALLOWED_AUDIO_MIMES = {
    'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/webm',
    'audio/aac', 'audio/flac', 'audio/x-wav',
}

ALLOWED_VIDEO_MIMES = {
    'video/mp4', 'video/webm', 'video/ogg', 'video/quicktime',
    'video/x-msvideo', 'video/x-matroska',
}

ALL_ALLOWED_MIMES = ALLOWED_IMAGE_MIMES | ALLOWED_AUDIO_MIMES | ALLOWED_VIDEO_MIMES

ALLOWED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
    # Audio
    '.mp3', '.wav', '.ogg', '.aac', '.flac', '.webm',
    # Video
    '.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# --- Model choices ---
CONVERSATION_STATUS_CHOICES = [
    ('active', 'Active'),
    ('diagnosed', 'Diagnosed'),
    ('booked', 'Booked'),
]

MESSAGE_ROLE_CHOICES = [
    ('user', 'User'),
    ('assistant', 'Assistant'),
    ('system', 'System'),
]

MESSAGE_TYPE_CHOICES = [
    ('text', 'Text'),
    ('image', 'Image'),
    ('audio', 'Audio'),
    ('video', 'Video'),
]

SEVERITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

BOOKING_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
]

# Minimum user messages before diagnosis can be generated
MIN_MESSAGES_FOR_DIAGNOSIS = 2

# Maximum messages to include in AI context
MAX_CONTEXT_MESSAGES = 10

