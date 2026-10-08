# Rendimiento e idiomas

Conservar look and feel, tipografía, encuadre y proporciones. Generar WebP a dimensiones útiles, sin sustituir originales ni cambiar recorte CSS. Usar retrato suficiente para ampliación CSS y optimizar portadas conservando transparencia. Agregar dimensiones, `decoding=async`, prioridad al retrato y carga diferida solo a imágenes secundarias. Evitar frameworks, fuentes remotas y librerías innecesarias.

Medir bytes antes/después y separar reducción de peso de velocidad real. No llamar Lighthouse a una suma de tamaños ni dar un score sin ejecutarlo. Mantener originales y rutas QR estables. Revisar móvil y teclado cuando haya navegador.

Crear español en `/` e inglés en `/en.html`, selector ES/EN con `aria-current`, `lang`, canonical propio y `hreflang`. Traducir bio, acciones, ayudas, errores, accesibilidad y metadatos. Conservar nombres, títulos publicados, email, teléfonos y destinos. No afirmar libros/PDF traducidos por traducir el botón. Evitar detección automática que cambie el destino del QR.

Generar ambas páginas antes de `build_offline.py`, que produce las tarjetas offline de ambos idiomas. Comprobar contactos consistentes. La firma usa el idioma solicitado; generar variantes si se piden.
