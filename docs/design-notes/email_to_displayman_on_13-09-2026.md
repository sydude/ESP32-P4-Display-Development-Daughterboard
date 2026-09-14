Dear Anson,

Thank you for confirming with your engineering team that the supplied two-lane initialization file is correct for KD068HDFID009-C009A.
We are now finalizing the interface and power design for this exact module and need a few additional engineering confirmations:

- Please confirm the correct absolute-maximum rating for LCD IOVCC. The datasheet absolute-maximum table shows 1.68 V max, while the DC characteristics table allows 1.65–3.3 V and the supplied initialization file specifies IOVCC = 1.8 V. Is 1.8 V nominal explicitly approved for KD068HDFID009-C009A?
- In the LCD power-on/off sequence, does “VDDI” refer to connector pin 3 IOVCC? Please also confirm the required power-up and power-down ordering/timing.
- For the supplied 600 × 1280, 55 MHz, 2-lane configuration, please confirm:
	- required DSI pixel format
	- required video mode
required lane bit rate
continuous or non-continuous clock
supported minimum and maximum D-PHY lane rate
The datasheet D-PHY table gives 2×UI = 4–25 ns. Please confirm whether this table is correct for this exact module.
Please provide the LED backlight forward-voltage minimum and maximum at 240 mA over temperature, and confirm that 240 mA is the total current for the internal 6S4P backlight array.
Please explain the source-driver/source-to-glass mapping between the confirmed RSOX(600) configuration and the 480-pixel physical glass. Specifically, what happens to the additional 120 horizontal source positions, and does the host need to generate any black columns?
Please confirm the 40-pin LCD and 8-pin touch FPC contact-side/orientation requirements and recommended mating connector/cable configuration.
Please confirm the GT9271 INT electrical type after initialization and the recommended default 7-bit I2C address for this module.


Thank you,

Sy A.
