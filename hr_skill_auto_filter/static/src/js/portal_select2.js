/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

const CustomSelectBox = publicWidget.Widget.extend({
  selector: "select.select_box_test",
  disabledInEditableMode: true,

  async start() {
    await this._super(...arguments);
    this._initSelect2();
  },

  _initSelect2() {
    this.$el.select2({
      placeholder: "Select Skills...",
      allowClear: true,
      closeOnSelect: true,
    });
  },

  // Override destroy instead of using event handler
  destroy() {
    this._destroySelect2();
    this._super(...arguments);
  },

  _destroySelect2() {
    if (this.$el && this.$el.hasClass("select2-hidden-accessible")) {
      this.$el.select2("destroy");
    }
  },
});

publicWidget.registry.CustomSelectBox = CustomSelectBox;
