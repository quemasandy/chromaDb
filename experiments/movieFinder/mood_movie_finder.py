import chromadb
from documents_data import documents

class MoodMovieFinder:
    def __init__(self):
        # Usar modo persistente para guardar datos
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("mood_movies")
        
        # Cargar películas si la colección está vacía
        self._load_movies()
    
    def _load_movies(self):
        """Cargar películas en la base de datos si no existen"""
        try:
            # Verificar si ya hay datos
            existing_data = self.collection.count()
            if existing_data == 0:
                print("🎬 Cargando base de datos de películas...")
                
                # Crear descripciones enriquecidas con emociones para cada película
                enriched_documents = []
                for doc in documents:
                    # Extraer información básica
                    movie_text = doc["text"]
                    
                    # Agregar palabras clave emocionales basadas en el contenido
                    emotional_keywords = self._extract_emotional_keywords(movie_text)
                    
                    # Crear texto enriquecido
                    enriched_text = f"{movie_text} | Emotional Keywords: {emotional_keywords}"
                    enriched_documents.append(enriched_text)
                
                # Insertar en ChromaDB
                self.collection.upsert(
                    ids=[doc["id"] for doc in documents],
                    documents=enriched_documents
                )
                print(f"✅ {len(documents)} películas cargadas exitosamente!")
            else:
                print(f"📚 Base de datos ya contiene {existing_data} películas")
        except Exception as e:
            print(f"❌ Error cargando películas: {e}")
    
    def _extract_emotional_keywords(self, movie_text):
        """Extraer palabras clave emocionales del texto de la película"""
        # Mapeo de géneros y temas a emociones
        emotion_mapping = {
            # Estados de ánimo positivos
            "happy": ["comedy", "musical", "adventure", "family", "animated", "feel-good", "uplifting", "joy", "celebration"],
            "excited": ["action", "adventure", "superhero", "thriller", "fast-paced", "adrenaline", "explosive", "epic"],
            "romantic": ["romance", "love story", "passionate", "heartwarming", "relationship", "wedding", "couple"],
            "inspired": ["biography", "true story", "overcoming", "triumph", "hero", "achievement", "success", "motivational"],
            "nostalgic": ["period piece", "classic", "childhood", "memories", "vintage", "retro", "coming-of-age"],
            
            # Estados de ánimo contemplativos
            "thoughtful": ["drama", "philosophical", "complex", "deep", "meaningful", "introspective", "thought-provoking"],
            "curious": ["mystery", "science-fiction", "documentary", "exploration", "discovery", "investigation"],
            "adventurous": ["adventure", "exploration", "journey", "quest", "travel", "exotic", "unknown"],
            
            # Estados de ánimo intensos
            "tense": ["thriller", "suspense", "psychological", "edge-of-seat", "nail-biting", "intense"],
            "scared": ["horror", "supernatural", "frightening", "creepy", "terrifying", "haunting"],
            "angry": ["revenge", "justice", "corruption", "betrayal", "injustice", "fighting"],
            
            # Estados de ánimo melancólicos
            "sad": ["tragedy", "loss", "grief", "heartbreak", "emotional", "tear-jerker", "melancholy"],
            "lonely": ["isolation", "solitude", "alienation", "abandoned", "alone", "outcast"],
            "reflective": ["life lessons", "mortality", "aging", "wisdom", "retrospective", "contemplative"]
        }
        
        keywords = []
        movie_lower = movie_text.lower()
        
        for emotion, terms in emotion_mapping.items():
            for term in terms:
                if term in movie_lower:
                    keywords.append(emotion)
                    break
        
        return ", ".join(set(keywords)) if keywords else "general entertainment"
    
    def find_movie_by_mood(self, mood_description, num_results=3):
        """Buscar películas basadas en descripción de estado de ánimo"""
        print(f"\n🎯 Buscando películas para: '{mood_description}'")
        print("-" * 50)
        
        try:
            # Realizar búsqueda semántica
            results = self.collection.query(
                query_texts=[mood_description],
                n_results=num_results
            )
            
            if not results["documents"] or not results["documents"][0]:
                print("❌ No se encontraron películas para ese estado de ánimo")
                return
            
            # Mostrar resultados
            for i, (doc_id, document, distance) in enumerate(zip(
                results["ids"][0], 
                results["documents"][0], 
                results["distances"][0]
            ), 1):
                # Extraer información de la película
                movie_info = self._parse_movie_info(document)
                
                print(f"\n🎬 Recomendación #{i}")
                print(f"📽️  Título: {movie_info['title']}")
                print(f"🎭 Género: {movie_info['genre']}")
                print(f"⭐ Rating: {movie_info['rating']}")
                print(f"⏱️  Duración: {movie_info['runtime']}")
                print(f"🎯 Relevancia: {self._get_relevance_text(distance)}")
                print(f"📝 Sinopsis: {movie_info['synopsis'][:200]}...")
                
                if i < num_results:
                    print("-" * 30)
                    
        except Exception as e:
            print(f"❌ Error en la búsqueda: {e}")
    
    def _parse_movie_info(self, movie_text):
        """Extraer información estructurada del texto de la película"""
        try:
            # Dividir el texto en partes
            parts = movie_text.split(" | ")
            
            # Extraer título (primera parte antes del año)
            title_part = parts[0] if parts else movie_text
            title = title_part.split(" (")[0] if " (" in title_part else title_part
            
            # Buscar información específica
            genre = "N/A"
            rating = "N/A"
            runtime = "N/A"
            synopsis = "N/A"
            
            for part in parts:
                if part.startswith("Genre:"):
                    genre = part.replace("Genre:", "").strip()
                elif part.startswith("Runtime:"):
                    runtime = part.replace("Runtime:", "").strip()
                elif part.startswith("IMDB:"):
                    rating = part.replace("IMDB:", "").strip()
                elif part.startswith("Synopsis:"):
                    synopsis = part.replace("Synopsis:", "").strip()
            
            return {
                "title": title,
                "genre": genre,
                "rating": rating,
                "runtime": runtime,
                "synopsis": synopsis
            }
        except:
            return {
                "title": "Película",
                "genre": "N/A",
                "rating": "N/A", 
                "runtime": "N/A",
                "synopsis": movie_text[:200]
            }
    
    def _get_relevance_text(self, distance):
        """Convertir distancia numérica a texto de relevancia"""
        if distance < 0.3:
            return "🎯 Perfecta coincidencia"
        elif distance < 0.5:
            return "✅ Muy buena coincidencia"
        elif distance < 0.7:
            return "👍 Buena coincidencia"
        else:
            return "🤔 Coincidencia moderada"
    
    def get_mood_suggestions(self):
        """Mostrar ejemplos de estados de ánimo que el usuario puede usar"""
        mood_examples = {
            "😊 Estados de ánimo positivos": [
                "Me siento feliz y quiero reír",
                "Estoy emocionado y quiero acción",
                "Quiero algo romántico y tierno",
                "Necesito inspiración y motivación"
            ],
            "🤔 Estados contemplativos": [
                "Quiero algo que me haga pensar",
                "Estoy curioso y quiero aprender",
                "Tengo ganas de aventura",
                "Quiero algo nostálgico"
            ],
            "😰 Estados intensos": [
                "Quiero algo que me mantenga en tensión",
                "Estoy de humor para algo de miedo",
                "Necesito desahogar mi enojo"
            ],
            "😢 Estados melancólicos": [
                "Estoy triste y quiero llorar",
                "Me siento solo",
                "Quiero reflexionar sobre la vida"
            ]
        }
        
        print("\n💡 Ejemplos de estados de ánimo que puedes usar:")
        print("=" * 60)
        
        for category, examples in mood_examples.items():
            print(f"\n{category}:")
            for example in examples:
                print(f"  • {example}")

def main():
    """Función principal para ejecutar el buscador de películas por estado de ánimo"""
    print("🎬 ¡Bienvenido al Buscador de Películas por Estado de Ánimo! 🎭")
    print("=" * 60)
    
    # Inicializar el buscador
    finder = MoodMovieFinder()
    
    while True:
        print("\n¿Qué te gustaría hacer?")
        print("1. Buscar película por estado de ánimo")
        print("2. Ver ejemplos de estados de ánimo")
        print("3. Salir")
        
        choice = input("\nElige una opción (1-3): ").strip()
        
        if choice == "1":
            mood = input("\n💭 Describe cómo te sientes o qué tipo de película quieres: ").strip()
            if mood:
                num_results = input("¿Cuántas recomendaciones quieres? (1-5, por defecto 3): ").strip()
                try:
                    num_results = int(num_results) if num_results else 3
                    num_results = max(1, min(5, num_results))  # Limitar entre 1 y 5
                except:
                    num_results = 3
                
                finder.find_movie_by_mood(mood, num_results)
            else:
                print("❌ Por favor describe tu estado de ánimo")
        
        elif choice == "2":
            finder.get_mood_suggestions()
        
        elif choice == "3":
            print("\n🎬 ¡Gracias por usar el Buscador de Películas! ¡Disfruta tu película! 🍿")
            break
        
        else:
            print("❌ Opción inválida. Por favor elige 1, 2 o 3.")

if __name__ == "__main__":
    main() 