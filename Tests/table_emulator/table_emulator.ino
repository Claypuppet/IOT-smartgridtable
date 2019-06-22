/**
   Smart Grid Table Emulator Sketch
*/

#include "config.h"
#include <MySensors.h>
#include "protocol.h"

char received_data;
bool new_data = false;

void presentation()
{
  present(TABLE_PART_ID, S_CUSTOM);
}

void setup()
{
} // End setup()

void loop()
{
  Serial.println("Smart Grid Table Emulator\n");
  Serial.println("Available options:");
  Serial.println("m - module menu");
  
  listen_for_serial_input();
  send_message();
} // End loop()

void send_message()
{
  if (new_data == true)
  {
    uint8_t selected_menu = 0;
    if (received_data == 'm') /* Modules menu */
    {
      if (user_wants_to_place_something())
      {
        change_module(select_module_location() - '0', select_module_type());
      }
      else
      {
        change_module(select_module_location() - '0', 0);
      }
    }
  }
} // End send_message()

bool user_wants_to_place_something()
{
  Serial.println("Do you want to (p)lace, or (r)emove?");
  listen_for_serial_input();
  if (received_data == 'p')
  {
    return true;
  }
  else if (received_data == 'r')
  {
    return false;
  }
  else
  {
    Serial.println("Enter either 'p' to place or 'r' to remove");
    return user_wants_to_place_something();
  }
}

uint8_t select_module_location()
{
  Serial.println("Select a module location:\n");
  Serial.println("--------------------------");
  Serial.println("|          |  |          |");
  Serial.println("|    [1]----------[2]    |");
  Serial.println("|        /      \\        |");
  Serial.println("| [0]---|        |---[3] |");
  Serial.println("|        \\      /        |");
  Serial.println("|    [5]----------[4]    |");
  Serial.println("|          |  |          |");
  Serial.println("--------------------------");

  listen_for_serial_input();
  return received_data;
}

uint32_t select_module_type()
{
  Serial.println("Which module do you want to place?\n");
  Serial.println("---- HIGH VOLTAGE ----");
  Serial.println("a - Solar plant");
  Serial.println("b - Wind park");
  Serial.println("c - Power plant");
  Serial.println("---- MEDIUM VOLTAGE ----");
  Serial.println("d - Factory 1");
  Serial.println("e - Factory 2 (with wind turbine)");
  Serial.println("f - Factory 3 (with wind turbine)");
  Serial.println("---- LOW VOLTAGE ----");
  Serial.println("g - Residential Area 1 (with wind turbine)");
  Serial.println("h - Residential Area 2 (with wind turbine)");
  Serial.println("i - Residential Area 3 (with wind turbine)");
  Serial.println("j - Residential Area 4 (with wind turbine)");
  Serial.println("k - Residential Area 5 (with solar panels and electric vehicle)");
  Serial.println("l - Residential Area 6 (with solar panels and electric vehicle)");

  listen_for_serial_input();

  switch (received_data)
  {
    case 'a':
      return 2090432304;
      break;
    case 'b':
      return 441033275;
      break;
    case 'c':
      return 448705851;
      break;
    case 'd':
      return 444756283;
      break;
    case 'e':
      return 1945520896;
      break;
    case 'f':
      return 1947426314;
      break;
    case 'g':
      return 2090677472;
      break;
    case 'h':
      return 1945556720;
      break;
    case 'i':
      return 1945746272;
      break;
    case 'j':
      return 439742523;
      break;
    case 'k':
      return 1946118352;
      break;
    case 'l':
      return 1946006704;
      break;
    default:
      break;
  }
}

void listen_for_serial_input()
{
  while (Serial.available() == 0) {}
  received_data = Serial.read();
  new_data = true;
} // End listen_for_serial_input()

// Handles incoming message from main-controller. This is a built-in function from the MySensors library
void receive(const MyMessage &msg)
{
  if (msg.type == REBOOT_BOSS_AND_HELPER_MSG)
  {
    Serial.println("Reboot command received from maincontroller");
  }
} // End receive()
