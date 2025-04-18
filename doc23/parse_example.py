def parse_legal_document(text):
    # Expresiones regulares para identificar secciones
    book_pattern = r"^(LIBRO|LBRO)\s+[^\n]+"
    title_pattern = r"^TITULO\s+[^\n]+"
    chapter_pattern = r"^CAPITULO\s+[^\n]+"
    article_pattern = r"^ARTICULO\s+(\d+-?[A-Z]?)\.\s*(.+)"

    # Estructura principal
    structure = {"title": "", "description": "", "sections": []}
    current_book = None
    current_title = None
    current_chapter = None
    current_article = None

    for line in text.split("\n"):
        line = line.strip()

        # Detectar libros
        book_match = re.match(book_pattern, line)
        if book_match:
            current_book = {
                "title": book_match.group(0),
                "description": "",
                "sections": [],
                "articles": [],
            }
            structure["sections"].append(current_book)
            current_title = None
            current_chapter = None
            current_article = None
            continue

        # Detectar títulos
        title_match = re.match(title_pattern, line)
        if title_match and current_book:
            current_title = {
                "title": title_match.group(0),
                "description": "",
                "sections": [],
                "articles": [],
            }
            current_book["sections"].append(current_title)
            current_chapter = None
            current_article = None
            continue

        # Detectar capítulos
        chapter_match = re.match(chapter_pattern, line)
        if chapter_match and current_title:
            current_chapter = {
                "title": chapter_match.group(0),
                "description": "",
                "articles": [],
            }
            current_title["sections"].append(current_chapter)
            current_article = None
            continue

        # Detectar artículos (con sufijos opcionales)
        article_match = re.match(article_pattern, line)
        if article_match:
            article = {
                "title": f"ARTICULO {article_match.group(1)}",
                "content": article_match.group(
                    2
                ),  # Captura todo el contenido inicial del artículo
            }

            # Si hay un capítulo actual, agregar el artículo dentro de él
            if current_chapter:
                current_chapter["articles"].append(article)
            # Si no hay un capítulo, el artículo pertenece directamente al título
            elif current_title:
                current_title["articles"].append(article)

            current_article = (
                article  # Mantener referencia para agregar contenido adicional
            )
            continue

        # Si encontramos contenido adicional para el artículo actual
        if current_article:
            current_article["content"] += (
                " " + line
            )  # Agregar contenido adicional al artículo
        elif current_chapter:
            current_chapter["description"] += " " + line
        elif current_title:
            current_title["description"] += " " + line
        elif current_book:
            current_book["description"] += " " + line
        else:
            structure["description"] += " " + line

    return structure
