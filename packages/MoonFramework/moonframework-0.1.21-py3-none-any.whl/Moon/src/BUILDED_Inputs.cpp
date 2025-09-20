/////////////////////////////////////////////////////////////////////////////////////////////////
/// Модуль предоставляющий базовый интерфейс для работы с вводом
/////////////////////////////////////////////////////////////////////////////////////////////////
#include "SFML/Window/Keyboard.hpp"
#include "SFML/Window/Mouse.hpp"
#include "SFML/Graphics/RenderWindow.hpp"
#include "SFML/System/Vector2.hpp"

#define MOON_API __declspec(dllexport)

// ==============================================================================================
// БЛОК ВНЕШНЕГО C-ИНТЕРФЕЙСА (экспортируемые функции)
// ==============================================================================================

extern "C" {

    // ==========================================================================================
    // ФУНКЦИИ ДЛЯ РАБОТЫ С КЛАВИАТУРОЙ
    // ==========================================================================================

    /**
     * @brief Проверяет, нажата ли указанная клавиша в данный момент
     * @param key Код клавиши (из перечисления sf::Keyboard::Key)
     * @return true если клавиша нажата, false в противном случае
     */
    MOON_API bool _Keyboard_IsKeyPressed(int key) {
        return sf::Keyboard::isKeyPressed(static_cast<sf::Keyboard::Key>(key));
    }

    /**
     * @brief Показывает или скрывает виртуальную клавиатуру (актуально для мобильных устройств)
     * @param visible true - показать клавиатуру, false - скрыть
     */
    MOON_API void _Keyboard_SetVirtualKeyboardVisible(bool visible) {
        sf::Keyboard::setVirtualKeyboardVisible(visible);
    }

    // ==========================================================================================
    // ФУНКЦИИ ДЛЯ РАБОТЫ С МЫШЬЮ
    // ==========================================================================================

    /**
     * @brief Проверяет, нажата ли указанная кнопка мыши в данный момент
     * @param button Код кнопки мыши (из перечисления sf::Mouse::Button)
     * @return true если кнопка нажата, false в противном случае
     */
    MOON_API bool _Mouse_IsButtonPressed(int button) {
        return sf::Mouse::isButtonPressed(static_cast<sf::Mouse::Button>(button));
    }

    /**
     * @brief Возвращает текущую координату X курсора мыши в глобальных координатах экрана
     * @return Координата X курсора мыши
     */
    MOON_API int _Mouse_GetPositionX() {
        return sf::Mouse::getPosition().x;
    }

    /**
     * @brief Возвращает текущую координату Y курсора мыши в глобальных координатах экрана
     * @return Координата Y курсора мыши
     */
    MOON_API int _Mouse_GetPositionY() {
        return sf::Mouse::getPosition().y;
    }

    /**
     * @brief Возвращает текущую координату X курсора мыши относительно окна
     * @param window Указатель на объект окна RenderWindow
     * @return Координата X курсора мыши относительно окна
     */
    MOON_API int _Mouse_GetPositionXWindow(sf::RenderWindow* window) {
        return sf::Mouse::getPosition(*window).x;
    }

    /**
     * @brief Возвращает текущую координату Y курсора мыши относительно окна
     * @param window Указатель на объект окна RenderWindow
     * @return Координата Y курсора мыши относительно окна
     */
    MOON_API int _Mouse_GetPositionYWindow(sf::RenderWindow* window) {
        return sf::Mouse::getPosition(*window).y;
    }

    /**
     * @brief Устанавливает позицию курсора мыши в глобальных координатах экрана
     * @param x Координата X для установки
     * @param y Координата Y для установки
     */
    MOON_API void _Mouse_SetPosition(int x, int y) {
        sf::Mouse::setPosition(sf::Vector2i(x, y));
    }

    /**
     * @brief Устанавливает позицию курсора мыши относительно окна
     * @param x Координата X для установки относительно окна
     * @param y Координата Y для установки относительно окна
     * @param window Указатель на объект окна RenderWindow
     */
    MOON_API void _Mouse_SetPositionWindow(int x, int y, sf::RenderWindow* window) {
        sf::Mouse::setPosition(sf::Vector2i(x, y), *window);
    }


} // extern "C"

// ==============================================================================================
// КОНЕЦ ФАЙЛА
// ==============================================================================================
