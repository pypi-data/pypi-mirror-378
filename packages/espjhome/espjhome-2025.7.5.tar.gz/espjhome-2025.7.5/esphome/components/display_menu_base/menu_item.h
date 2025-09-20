#pragma once

#include "esphome/core/defines.h"
#include "esphome/core/automation.h"

#ifdef USE_BINARY_SENSOR
#include "esphome/components/binary_sensor/binary_sensor.h"
#endif
#ifdef USE_NUMBER
#include "esphome/components/number/number.h"
#endif
#ifdef USE_SELECT
#include "esphome/components/select/select.h"
#endif
#ifdef USE_SWITCH
#include "esphome/components/switch/switch.h"
#endif

#ifdef USE_GROUPS
#include "esphome/components/groups/groups.h"
#endif

#include <vector>
#include "esphome/core/log.h"

namespace esphome {
namespace display_menu_base {

enum MenuItemType {
  MENU_ITEM_LABEL,
  MENU_ITEM_MENU,
  MENU_ITEM_BACK,
  MENU_ITEM_SELECT,
  MENU_ITEM_NUMBER,
  MENU_ITEM_SWITCH,
  MENU_ITEM_COMMAND,
  MENU_ITEM_CUSTOM,
  MENU_ITEM_BINARY_SENSOR,
  MENU_ITEM_VALUE
};

/// @brief Returns a string representation of a menu item type suitable for logging
const LogString *menu_item_type_to_string(MenuItemType type);

class MenuItem;
class MenuItemMenu;
using value_getter_t = std::function<std::string(const MenuItem *)>;

class MenuItem {
 public:
  explicit MenuItem(MenuItemType t) : item_type_(t) {}
  virtual ~MenuItem() {}
  void set_parent(MenuItem *parent) { this->parent_ = parent; }
  MenuItem *get_parent() { return this->parent_; }
  MenuItemType get_type() const { return this->item_type_; }
  template<typename V> void set_text(V val) { this->text_ = val; }
  void add_on_enter_callback(std::function<void()> &&cb) { this->on_enter_callbacks_.add(std::move(cb)); }
  void add_on_leave_callback(std::function<void()> &&cb) { this->on_leave_callbacks_.add(std::move(cb)); }
  void add_on_value_callback(std::function<void()> &&cb) { this->on_value_callbacks_.add(std::move(cb)); }

  std::string get_text() const { return const_cast<MenuItem *>(this)->text_.value(this); }
  virtual bool get_immediate_edit() const { return false; }

  virtual bool has_value() const { return false; }
  virtual std::string get_value_text() const { return ""; }

  void set_internal_items_flag(bool val) { this->has_internal_items_ = val; }
  bool has_internal_items() { return this->has_internal_items_; }

  void add_item(MenuItem *item) {
    item->set_parent(this);
    this->items_.push_back(item);
  }

  size_t items_size() const { return this->items_.size(); }
  MenuItem *get_item(size_t i) const { return this->items_[i]; }

  virtual bool select_next() { return false; }
  virtual bool select_prev() { return false; }

  void on_enter();
  void on_leave();

 protected:
  void on_value_();

  MenuItemType item_type_;
  MenuItem *parent_{nullptr};
  TemplatableValue<std::string, const MenuItem *> text_;

  CallbackManager<void()> on_enter_callbacks_{};
  CallbackManager<void()> on_leave_callbacks_{};
  CallbackManager<void()> on_value_callbacks_{};

  std::vector<MenuItem *> items_;
  bool has_internal_items_{false};
};

class MenuItemValueBase : public MenuItem {
 public:
  explicit MenuItemValueBase(MenuItemType t) : MenuItem(t) {}
  void set_value_lambda(value_getter_t &&getter) { this->value_getter_ = getter; }
  std::string get_value_text() const override;
  bool has_value() const override { return this->value_getter_.has_value(); }

 protected:
  optional<value_getter_t> value_getter_{};
};

class MenuItemMenu : public MenuItemValueBase {
 public:
  using generate_lambda_t = std::function<size_t(MenuItemMenu *menu)>;
  explicit MenuItemMenu() : MenuItemValueBase(MENU_ITEM_MENU) {}
  ~MenuItemMenu() override { clear_items(); }
  void add_generated_items(MenuItem *item) {
    item->set_parent(this);
    this->items_.push_back(item);
  }
  size_t generate() {
    if (lambda_)
      return lambda_(this);
    return 0;
  }
  void set_generate_lambda(generate_lambda_t &&lambda) { this->lambda_ = lambda; }

  bool is_generated() { return this->generated_; }
  void set_was_generated(bool val) { this->generated_ = val; }

  bool is_generate_on_enter() { return this->generate_on_enter_; }
  void set_generate_on_enter(bool val) { this->generate_on_enter_ = val; }

  void clear_items() {
    for (auto *item : this->items_) {
      delete item;
    }
    this->items_.clear();
    this->generated_ = false;
  }

#ifdef USE_GROUPS
  void add_group(groups::Group *group) { this->groups_.push_back(group); }
  const std::vector<groups::Group *> &groups() { return groups_; }
#endif
 protected:
#ifdef USE_GROUPS
  std::vector<groups::Group *> groups_;
#endif
  generate_lambda_t lambda_;
  bool generated_{false};
  bool generate_on_enter_{false};
};

class MenuItemEditable : public MenuItemValueBase {
 public:
  explicit MenuItemEditable(MenuItemType t) : MenuItemValueBase(t) {}
  void set_immediate_edit(bool val) { this->immediate_edit_ = val; }
  bool get_immediate_edit() const override { return this->immediate_edit_; }

 protected:
  bool immediate_edit_{false};
};

#ifdef USE_BINARY_SENSOR
class MenuItemBinarySensor : public MenuItem {
 public:
  explicit MenuItemBinarySensor() : MenuItem(MENU_ITEM_BINARY_SENSOR) {}
  void set_binary_sensor_variable(binary_sensor::BinarySensor *var) { this->binary_sensor_ = var; }
  void set_on_text(const char *t) { this->on_text_ = StringRef(t); }
  void set_off_text(const char *t) { this->off_text_ = StringRef(t); }
  void set_no_data_text(const char *t) { this->no_data_text_ = StringRef(t); }

  bool has_value() const override { return true; }
  std::string get_value_text() const override;

 protected:
  binary_sensor::BinarySensor *binary_sensor_{nullptr};
  StringRef on_text_;
  StringRef off_text_;
  StringRef no_data_text_;
};
#endif

#ifdef USE_SELECT
class MenuItemSelect : public MenuItemEditable {
 public:
  explicit MenuItemSelect() : MenuItemEditable(MENU_ITEM_SELECT) {}
  void set_select_variable(select::Select *var) { this->select_var_ = var; }

  bool has_value() const override { return true; }
  std::string get_value_text() const override;

  bool select_next() override;
  bool select_prev() override;

 protected:
  select::Select *select_var_{nullptr};
};
#endif

#ifdef USE_NUMBER
class MenuItemNumber : public MenuItemEditable {
 public:
  explicit MenuItemNumber() : MenuItemEditable(MENU_ITEM_NUMBER) {}
  void set_number_variable(number::Number *var) { this->number_var_ = var; }
  void set_format(const std::string &fmt) { this->format_ = fmt; }

  bool has_value() const override { return true; }
  std::string get_value_text() const override;

  bool select_next() override;
  bool select_prev() override;

 protected:
  float get_number_value_() const;

  number::Number *number_var_{nullptr};
  std::string format_;
};
#endif

#ifdef USE_SWITCH
class MenuItemSwitch : public MenuItemEditable {
 public:
  explicit MenuItemSwitch() : MenuItemEditable(MENU_ITEM_SWITCH) {}
  void set_switch_variable(switch_::Switch *var) { this->switch_var_ = var; }
  void set_on_text(const std::string &t) { this->switch_on_text_ = t; }
  void set_off_text(const std::string &t) { this->switch_off_text_ = t; }

  bool has_value() const override { return true; }
  std::string get_value_text() const override;

  bool select_next() override;
  bool select_prev() override;

 protected:
  bool get_switch_state_() const;
  bool toggle_switch_();

  switch_::Switch *switch_var_{nullptr};
  std::string switch_on_text_;
  std::string switch_off_text_;
};
#endif

class MenuItemCommand : public MenuItem {
 public:
  explicit MenuItemCommand() : MenuItem(MENU_ITEM_COMMAND) {}

  bool select_next() override;
  bool select_prev() override;
};

class MenuItemCustom : public MenuItemEditable {
 public:
  explicit MenuItemCustom() : MenuItemEditable(MENU_ITEM_CUSTOM) {}
  void add_on_next_callback(std::function<void()> &&cb) { this->on_next_callbacks_.add(std::move(cb)); }
  void add_on_prev_callback(std::function<void()> &&cb) { this->on_prev_callbacks_.add(std::move(cb)); }

  bool has_value() const override { return this->value_getter_.has_value(); }

  bool select_next() override;
  bool select_prev() override;

 protected:
  void on_next_();
  void on_prev_();

  CallbackManager<void()> on_next_callbacks_{};
  CallbackManager<void()> on_prev_callbacks_{};
};

class MenuItemValue : public MenuItemValueBase {
 public:
  explicit MenuItemValue() : MenuItemValueBase(MENU_ITEM_VALUE) {}
};

}  // namespace display_menu_base
}  // namespace esphome
