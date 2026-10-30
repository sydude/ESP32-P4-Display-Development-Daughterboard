#include "soc/soc_caps.h"

#if SOC_MIPI_DSI_SUPPORTED

#include <inttypes.h>
#include <assert.h>
#include "esp_check.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_io.h"
#include "esp_ldo_regulator.h"
#include "esp_dma_utils.h"
#include "esp_lcd_mipi_dsi.h"
#include "esp_lcd_dsi.h"

#include "driver/i2c_master.h"

#define TEST_LCD_H_RES (480)
#define TEST_LCD_V_RES (1920)
#define TEST_LCD_BIT_PER_PIXEL (24)
#define TEST_PIN_NUM_LCD_RST (-1)
#define TEST_PIN_NUM_BK_LIGHT (-1) // set to -1 if not used
#define TEST_LCD_BK_LIGHT_ON_LEVEL (1)
#define TEST_LCD_BK_LIGHT_OFF_LEVEL !TEST_LCD_BK_LIGHT_ON_LEVEL

#if TEST_LCD_BIT_PER_PIXEL == 24
#define TEST_MIPI_DPI_PX_FORMAT (LCD_COLOR_PIXEL_FORMAT_RGB888)
#elif TEST_LCD_BIT_PER_PIXEL == 18
#define TEST_MIPI_DPI_PX_FORMAT (LCD_COLOR_PIXEL_FORMAT_RGB666)
#elif TEST_LCD_BIT_PER_PIXEL == 16
#define TEST_MIPI_DPI_PX_FORMAT (LCD_COLOR_PIXEL_FORMAT_RGB565)
#endif

#define TEST_DELAY_TIME_MS (3000)

#define TEST_MIPI_DSI_PHY_PWR_LDO_CHAN (3)
#define TEST_MIPI_DSI_PHY_PWR_LDO_VOLTAGE_MV (2500)

static char *TAG = "waveshare_display_touch";
static esp_ldo_channel_handle_t ldo_mipi_phy = NULL;
static esp_lcd_panel_handle_t panel_handle = NULL;
static esp_lcd_dsi_bus_handle_t mipi_dsi_bus = NULL;
static esp_lcd_panel_io_handle_t mipi_dbi_io = NULL;
static SemaphoreHandle_t refresh_finish = NULL;

IRAM_ATTR static bool test_notify_refresh_ready(esp_lcd_panel_handle_t panel, esp_lcd_dpi_panel_event_data_t *edata, void *user_ctx)
{
    SemaphoreHandle_t refresh_finish = (SemaphoreHandle_t)user_ctx;
    BaseType_t need_yield = pdFALSE;

    xSemaphoreGiveFromISR(refresh_finish, &need_yield);

    return (need_yield == pdTRUE);
}

static void test_init_lcd(void)
{
#if TEST_PIN_NUM_BK_LIGHT >= 0
    ESP_LOGI(TAG, "Turn on LCD backlight");
    gpio_config_t bk_gpio_config = {
        .mode = GPIO_MODE_OUTPUT,
        .pin_bit_mask = 1ULL << TEST_PIN_NUM_BK_LIGHT};
    ESP_ERROR_CHECK(gpio_config(&bk_gpio_config));
    ESP_ERROR_CHECK(gpio_set_level(TEST_PIN_NUM_BK_LIGHT, TEST_LCD_BK_LIGHT_ON_LEVEL));
#endif

    // Turn on the power for MIPI DSI PHY, so it can go from "No Power" state to "Shutdown" state
#ifdef TEST_MIPI_DSI_PHY_PWR_LDO_CHAN
    ESP_LOGI(TAG, "MIPI DSI PHY Powered on");
    esp_ldo_channel_config_t ldo_mipi_phy_config = {
        .chan_id = TEST_MIPI_DSI_PHY_PWR_LDO_CHAN,
        .voltage_mv = TEST_MIPI_DSI_PHY_PWR_LDO_VOLTAGE_MV,
    };
    ESP_ERROR_CHECK(esp_ldo_acquire_channel(&ldo_mipi_phy_config, &ldo_mipi_phy));
#endif

    ESP_LOGI(TAG, "Initialize MIPI DSI bus");
    esp_lcd_dsi_bus_config_t bus_config = DSI_PANEL_BUS_DSI_2CH_CONFIG();
    ESP_ERROR_CHECK(esp_lcd_new_dsi_bus(&bus_config, &mipi_dsi_bus));

    ESP_LOGI(TAG, "Install panel IO");
    esp_lcd_dbi_io_config_t dbi_config = DSI_PANEL_IO_DBI_CONFIG();
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_dbi(mipi_dsi_bus, &dbi_config, &mipi_dbi_io));

    ESP_LOGI(TAG, "Install LCD driver of dsi");
    esp_lcd_dpi_panel_config_t dpi_config = DSI_PANEL_DPI_8_8_INCH_CONFIG(TEST_MIPI_DPI_PX_FORMAT);
    dsi_vendor_config_t vendor_config = {
        .mipi_config = {
            .dsi_bus = mipi_dsi_bus,
            .dpi_config = &dpi_config,
        },
    };
    const esp_lcd_panel_dev_config_t panel_config = {
        .reset_gpio_num = TEST_PIN_NUM_LCD_RST,
        .rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB,
        .bits_per_pixel = TEST_LCD_BIT_PER_PIXEL,
        .vendor_config = &vendor_config,
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_dsi(mipi_dbi_io, &panel_config, &panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel_handle));

    refresh_finish = xSemaphoreCreateBinary();
    assert(refresh_finish != NULL);
    esp_lcd_dpi_panel_event_callbacks_t cbs = {
        .on_color_trans_done = test_notify_refresh_ready,
    };
    ESP_ERROR_CHECK(esp_lcd_dpi_panel_register_event_callbacks(panel_handle, &cbs, refresh_finish));
}

void app_main(void)
{
    ESP_LOGI(TAG, "Initialize LCD device");
    test_init_lcd();

    // Check for touch controller on the existing I2C bus
    i2c_master_bus_handle_t touch_bus = NULL;
    esp_err_t err = i2c_master_get_bus_handle(I2C_NUM_1, &touch_bus);

    if (err == ESP_OK) {
        const uint8_t addresses[] = {0x14, 0x5D, 0x41, 0x45};

        for (size_t i = 0; i < sizeof(addresses); i++) {
            err = i2c_master_probe(touch_bus, addresses[i], 100);
            ESP_LOGI(TAG, "I2C address 0x%02X: %s",
                    addresses[i], err == ESP_OK ? "FOUND" : "Not detected");
        }
    } else {
        ESP_LOGE(TAG, "Unable to access I2C bus: %s", esp_err_to_name(err));
    }
    ESP_LOGI(TAG, "Show color bar pattern drawn by hardware");
    ESP_ERROR_CHECK(esp_lcd_dpi_panel_set_pattern(panel_handle, MIPI_DSI_PATTERN_BAR_VERTICAL));

    // Connect to the GT9271 using the existing I2C bus
    i2c_master_bus_handle_t gt_bus;
    ESP_ERROR_CHECK(i2c_master_get_bus_handle(I2C_NUM_1, &gt_bus));

    i2c_device_config_t gt_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = 0x14,
        .scl_speed_hz = 100000,
    };
    i2c_master_dev_handle_t gt;
    ESP_ERROR_CHECK(i2c_master_bus_add_device(gt_bus, &gt_cfg, &gt));

    // Read the four-byte product ID
    uint8_t id_reg[] = {0x81, 0x40};
    char product_id[5] = {0};
    ESP_ERROR_CHECK(i2c_master_transmit_receive(
        gt, id_reg, 2, (uint8_t *)product_id, 4, 100));
    ESP_LOGI(TAG, "Touch controller product ID: %s", product_id);

    // Poll the GT9271 for touch events
    uint8_t status_reg[] = {0x81, 0x4E};
    uint8_t points_reg[] = {0x81, 0x4F};

    while (true) {
        uint8_t status = 0;
        esp_err_t result = i2c_master_transmit_receive(
            gt, status_reg, 2, &status, 1, 100);

        if (result == ESP_OK && (status & 0x80)) {
            uint8_t count = status & 0x0F;

            if (count > 0 && count <= 5) {
                uint8_t points[5 * 8];
                result = i2c_master_transmit_receive(
                    gt, points_reg, 2, points, count * 8, 100);

                if (result == ESP_OK) {
                    for (int i = 0; i < count; i++) {
                        uint8_t *p = &points[i * 8];
                        uint16_t x = p[1] | (p[2] << 8);
                        uint16_t y = p[3] | (p[4] << 8);

                        ESP_LOGI(TAG, "Finger %d: ID=%u X=%u Y=%u",
                                 i + 1, p[0], x, y);
                    }
                }
            }

            // Acknowledge the data so the controller can report new touches
            uint8_t clear[] = {0x81, 0x4E, 0x00};
            ESP_ERROR_CHECK(i2c_master_transmit(gt, clear, 3, 100));
        } else if (result != ESP_OK) {
            ESP_LOGW(TAG, "Touch read failed: %s", esp_err_to_name(result));
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
#endif
