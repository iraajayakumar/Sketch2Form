#include <MCUFRIEND_kbv.h>
#include <TouchScreen.h>

MCUFRIEND_kbv tft;
const int XP = 8, XM = A2, YP = A3, YM = 9; // 320x480 ID=0x9090
const int TS_LEFT = 134, TS_RT = 981, TS_TOP = 925, TS_BOT = 150;
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);
TSPoint tp;

#define MINPRESSURE 10
#define MAXPRESSURE 1000

uint16_t ID, currentcolor;
uint16_t oldcolor;
int16_t BOXSIZE;
int16_t PENRADIUS = 2.5;
uint8_t Orientation = 0; // PORTRAIT

// Colors
#define BLACK 0x0000
#define BLUE 0x001F
#define RED 0xF800
#define GREEN 0x07E0
#define CYAN 0x07FF
#define MAGENTA 0xF81F
#define YELLOW 0xFFE0
#define WHITE 0xFFFF

// Button Areas
#define DONE_Y_START 380
#define BTN_HEIGHT 40
#define BTN_WIDTH 120

bool isDrawing = false;

void drawUI() {
  tft.fillScreen(BLACK);

  // Color palette
  BOXSIZE = tft.width() / 6;
  tft.fillRect(0, 0, BOXSIZE, BOXSIZE, RED);
  tft.fillRect(BOXSIZE, 0, BOXSIZE, BOXSIZE, YELLOW);
  tft.fillRect(BOXSIZE * 2, 0, BOXSIZE, BOXSIZE, GREEN);
  tft.fillRect(BOXSIZE * 3, 0, BOXSIZE, BOXSIZE, CYAN);
  tft.fillRect(BOXSIZE * 4, 0, BOXSIZE, BOXSIZE, BLUE);
  tft.fillRect(BOXSIZE * 5, 0, BOXSIZE, BOXSIZE, MAGENTA);
  tft.drawRect(0, 0, BOXSIZE, BOXSIZE, WHITE);

  // Buttons
  tft.fillRect(10, DONE_Y_START, BTN_WIDTH, BTN_HEIGHT, GREEN);
  tft.fillRect(190, DONE_Y_START, BTN_WIDTH, BTN_HEIGHT, RED);
  tft.setTextColor(WHITE);
  tft.setTextSize(2);
  tft.setCursor(35, DONE_Y_START + 10);
  tft.print("DONE");
  tft.setCursor(215, DONE_Y_START + 10);
  tft.print("CLEAR");

  currentcolor = RED;
}

void setup() {
  Serial.begin(9600);
  tft.reset();
  ID = tft.readID();
  tft.begin(ID);
  tft.invertDisplay(true);
  tft.setRotation(Orientation);
  drawUI();
}

void loop() {
  tp = ts.getPoint();
  pinMode(XM, OUTPUT);
  pinMode(YP, OUTPUT);

  if (tp.z > MINPRESSURE && tp.z < MAXPRESSURE) {
    uint16_t xpos = map(tp.x, TS_LEFT, TS_RT, 0, tft.width());
    uint16_t ypos = map(tp.y, TS_TOP, TS_BOT, 0, tft.height());

    // 🟥 Color palette selection (top row)
    if (ypos < BOXSIZE) {
      oldcolor = currentcolor;
      int boxIndex = xpos / BOXSIZE;

      switch (boxIndex) {
        case 0: currentcolor = RED; break;
        case 1: currentcolor = YELLOW; break;
        case 2: currentcolor = GREEN; break;
        case 3: currentcolor = CYAN; break;
        case 4: currentcolor = BLUE; break;
        case 5: currentcolor = MAGENTA; break;
      }

      // Highlight selected color
      if (oldcolor != currentcolor) {
        tft.drawRect(boxIndex * BOXSIZE, 0, BOXSIZE, BOXSIZE, WHITE);
        int oldIndex = (oldcolor == RED) ? 0 :
                       (oldcolor == YELLOW) ? 1 :
                       (oldcolor == GREEN) ? 2 :
                       (oldcolor == CYAN) ? 3 :
                       (oldcolor == BLUE) ? 4 : 5;
        tft.drawRect(oldIndex * BOXSIZE, 0, BOXSIZE, BOXSIZE, BLACK);
      }
    }

    // ✅ Button area (DONE / CLEAR)
    else if (ypos > DONE_Y_START && ypos < DONE_Y_START + BTN_HEIGHT) {
      if (xpos < 130) {
        Serial.println("END_SHAPE");
        isDrawing = false;
      } else if (xpos > 180) {
        clearDrawing();
      }
    }

    // ✏️ Drawing area
    else if (ypos > BOXSIZE && ypos < DONE_Y_START) {
      tft.fillCircle(xpos, ypos, PENRADIUS, currentcolor);

      if (!isDrawing) {
        Serial.println("START_SHAPE");
        isDrawing = true;
      }

      Serial.print("{\"x\":");
      Serial.print(xpos);
      Serial.print(",\"y\":");
      Serial.print(ypos);
      Serial.print(",\"t\":");
      Serial.print(millis());
      Serial.print(",\"c\":");
      Serial.print(currentcolor);
      Serial.println("}");
    }
  }
}


void clearDrawing() {
  tft.fillRect(0, BOXSIZE, tft.width(), DONE_Y_START - BOXSIZE, BLACK);
  drawUI();
  Serial.println("CLEARED");
  isDrawing = false;
}
