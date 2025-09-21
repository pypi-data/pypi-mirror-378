"""
Module containing greetings in various native languages.
"""

GREETINGS = {
    'english': 'Hello World',
    'spanish': '¡Hola Mundo',
    'french': 'Bonjour le Monde',
    'german': 'Hallo Welt',
    'russian': 'Привет Мир',
    'chinese': '你好世界',
    'japanese': 'こんにちは世界',
    'hindi': 'नमस्ते दुनिया',
    'tamil' : 'வணக்கம் உலகம்',
    'telugu' : 'హలో వరల్డ్',
    'kannada' : 'ಹಲೋ ವರ್ಲ್ಡ್',
    'malayalam' : 'ഹലോ വേൾഡ്',
    'arabic': 'مرحبا بالعالم',
    'korean': '안녕하세요 세계',
    'turkish': 'Merhaba Dünya',
    'vietnamese': 'Xin chào Thế giới',
    'greek': 'Γειά σου Κόσμε',
    'thai': 'สวัสดีโลก'
}

def get_greeting(language='english'):
    """
    Get a hello world greeting in the specified language.
    
    Args:
        language (str): Language code (e.g., 'english', 'spanish')
    
    Returns:
        str: Greeting in the specified language
    """
    return GREETINGS.get(language.lower(), GREETINGS['english'])

def list_languages():
    """
    List all available languages.
    
    Returns:
        list: List of available language codes
    """
    return list(GREETINGS.keys())

def greet_all():
    """
    Print hello world in all available languages.
    """
    for lang, greeting in GREETINGS.items():
        print(f"{lang.title()}: {greeting}")