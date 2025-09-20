// Подключение необходимых заголовочных файлов SFML
#ifndef SFML_GRAPHICS_HPP
#include "SFML/Graphics.hpp"
#endif
#ifndef SFML_WINDOW_HPP
#include "SFML/Window.hpp"
#endif
#ifndef SFML_SYSTEM_HPP
#include "SFML/System.hpp"
#endif

// Установка кодировки для корректного отображения русских символов
#pragma execution_character_set("utf-8")

// ==============================================================================================
// БЛОК ОПРЕДЕЛЕНИЯ ТИПОВ ДАННЫХ
// ==============================================================================================

// Определение псевдонимов типов для удобства работы с указателями SFML
typedef sf::Font* FontPtr;    // Указатель на объект шрифта
typedef sf::Text* TextPtr;    // Указатель на объект текста

// ==============================================================================================
// БЛОК ВНЕШНЕГО C-ИНТЕРФЕЙСА (экспортируемые функции)
// ==============================================================================================

extern "C" {

    // ==========================================================================================
    // ФУНКЦИИ ДЛЯ РАБОТЫ СО ШРИФТАМИ
    // ==========================================================================================

    /**
     * @brief Загружает шрифт из файла
     * @param path Путь к файлу шрифта
     * @return Указатель на загруженный шрифт или nullptr в случае ошибки
     */
    __declspec(dllexport) FontPtr loadSystemFont(const char* path) {
        FontPtr font = new sf::Font();
        try {
            // Попытка загрузки шрифта из файла
            if (!font->loadFromFile(path)) {
                delete font;  // Важно: освобождаем память при неудачной загрузке
                return nullptr;
            }
        } catch (const std::exception& e) {
            delete font;  // Освобождаем память в случае исключения
            return nullptr;
        }
        // Отключаем сглаживание для более четкого отображения
        font->setSmooth(false);
        return font;
    }

    // ==========================================================================================
    // ФУНКЦИИ ДЛЯ СОЗДАНИЯ И УПРАВЛЕНИЯ ТЕКСТОМ
    // ==========================================================================================

    /**
     * @brief Создает объект текста с указанным шрифтом
     * @param font Указатель на шрифт
     * @return Указатель на созданный объект текста
     */
    __declspec(dllexport) TextPtr createText(FontPtr font) {
        TextPtr text = new sf::Text();
        text->setFont(*font);
        return text;
    }

    /**
     * @brief Устанавливает текстовое содержимое
     * @param text Указатель на объект текста
     * @param str Строка для отображения (в кодировке UTF-8)
     */
    __declspec(dllexport) void setText(TextPtr text, const char* str) {
        std::string std_str(str);
        // Преобразование из UTF-8 в внутренний формат SFML
        text->setString(sf::String::fromUtf8(std_str.begin(), std_str.end()));
    }

    /**
     * @brief Устанавливает размер символов текста
     * @param text Указатель на объект текста
     * @param size Размер шрифта в пикселях
     */
    __declspec(dllexport) void setTextSize(TextPtr text, int size) {
        text->setCharacterSize(size);
    }

    /**
     * @brief Устанавливает масштаб текста
     * @param text Указатель на объект текста
     * @param scaleX Масштаб по оси X
     * @param scaleY Масштаб по оси Y
     */
    __declspec(dllexport) void setTextScale(TextPtr text, float scaleX, float scaleY) {
        text->setScale(scaleX, scaleY);
    }

    /**
     * @brief Устанавливает цвет текста
     * @param text Указатель на объект текста
     * @param r Красная компонента цвета (0-255)
     * @param g Зеленая компонента цвета (0-255)
     * @param b Синяя компонента цвета (0-255)
     * @param a Альфа-компонента (прозрачность, 0-255)
     */
    __declspec(dllexport) void setTextColor(TextPtr text, int r, int g, int b, int a) {
        text->setFillColor(sf::Color(r, g, b, a));
    }

    /**
     * @brief Устанавливает позицию текста на экране
     * @param text Указатель на объект текста
     * @param x Координата X
     * @param y Координата Y
     */
    __declspec(dllexport) void setTextPosition(TextPtr text, float x, float y) {
        text->setPosition(x, y);
    }

    /**
     * @brief Устанавливает точку отсчета (origin) для трансформаций текста
     * @param text Указатель на объект текста
     * @param x Смещение по X относительно левого верхнего угла
     * @param y Смещение по Y относительно левого верхнего угла
     */
    __declspec(dllexport) void setTextOffset(TextPtr text, float x, float y) {
        text->setOrigin(x, y);
    }

    /**
     * @brief Устанавливает угол поворота текста
     * @param text Указатель на объект текста
     * @param angle Угол поворота в градусах
     */
    __declspec(dllexport) void setTextAngle(TextPtr text, float angle) {
        text->setRotation(angle);
    }

    /**
     * @brief Устанавливает стиль текста (жирный, курсив, подчеркнутый)
     * @param text Указатель на объект текста
     * @param style Комбинация флагов стиля из sf::Text::Style
     */
    __declspec(dllexport) void setStyle(TextPtr text, sf::Text::Style style) {
        text->setStyle(style);
    }

    /**
     * @brief Устанавливает цвет контура текста
     * @param text Указатель на объект текста
     * @param r Красная компонента цвета (0-255)
     * @param g Зеленая компонента цвета (0-255)
     * @param b Синяя компонента цвета (0-255)
     * @param a Альфа-компонента (прозрачность, 0-255)
     */
    __declspec(dllexport) void setOutlineColor(TextPtr text, int r, int g, int b, int a) {
        text->setOutlineColor(sf::Color(r, g, b, a));
    }

    /**
     * @brief Устанавливает толщину контура текста
     * @param text Указатель на объект текста
     * @param thickness Толщина контура в пикселях
     */
    __declspec(dllexport) void setOutlineThickness(TextPtr text, float thickness) {
        text->setOutlineThickness(thickness);
    }

    /**
     * @brief Устанавливает межбуквенное расстояние
     * @param text Указатель на объект текста
     * @param spacing Коэффициент межбуквенного расстояния
     */
    __declspec(dllexport) void setLetterSpacing(TextPtr text, float spacing) {
        text->setLetterSpacing(spacing);
    }

    // ==========================================================================================
    // ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ИНФОРМАЦИИ О ТЕКСТЕ
    // ==========================================================================================

    /**
     * @brief Возвращает ширину текста в пикселях
     * @param text Указатель на объект текста
     * @return Ширина текста с учетом всех трансформаций
     */
    __declspec(dllexport) double getTextWidth(TextPtr text) {
        return text->getGlobalBounds().width;
    }

    /**
     * @brief Возвращает высоту текста в пикселях
     * @param text Указатель на объект текста
     * @return Высота текста с учетом всех трансформаций
     */
    __declspec(dllexport) double getTextHeight(TextPtr text) {
        return text->getGlobalBounds().height;
    }

    // ==========================================================================================
    // ФУНКЦИИ ДЛЯ ИЗМЕНЕНИЯ СВОЙСТВ ТЕКСТА
    // ==========================================================================================

    /**
     * @brief Изменяет шрифт для текста
     * @param text Указатель на объект текста
     * @param font Указатель на новый шрифт
     */
    __declspec(dllexport) void setFont(TextPtr text, FontPtr font) {
        text->setFont(*font);
    }

} // extern "C"

// ==============================================================================================
// КОНЕЦ ФАЙЛА
// ==============================================================================================
