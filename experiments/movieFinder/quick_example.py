from mood_movie_finder import MoodMovieFinder

def quick_demo():
    """Demostración rápida del sistema de recomendación por estado de ánimo"""
    print("🎬 Demo rápido del Buscador de Películas por Estado de Ánimo")
    print("=" * 60)
    
    # Inicializar el buscador
    finder = MoodMovieFinder()
    
    # Ejemplos de búsquedas por diferentes estados de ánimo
    test_moods = [
        "Me siento triste y necesito llorar",
        "Quiero algo emocionante con mucha acción",
        "Estoy de humor romántico",
        "Necesito inspiración y motivación",
        "Quiero algo que me haga pensar profundamente"
    ]
    
    for mood in test_moods:
        print(f"\n{'='*60}")
        finder.find_movie_by_mood(mood, 2)  # 2 recomendaciones por estado de ánimo
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    quick_demo() 