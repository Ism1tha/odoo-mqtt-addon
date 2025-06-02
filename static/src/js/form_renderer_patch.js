/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { FormController } from '@web/views/form/form_controller';
import { onMounted, useEffect } from '@odoo/owl';

patch(FormController.prototype, {
  setup() {
    super.setup(...arguments);

    const updateButtonsVisibility = () => {
      const record = this.model.root;
      if (!record || !record.data) return;

      const buttons = document.querySelector('.o_statusbar_buttons');
      if (!buttons) return;

      for (const button of buttons.children) {
        const name = button.getAttribute('name');
        const shouldBeVisible =
          name === 'action_start_mqtt_processing' ||
          name === 'action_stop_mqtt_processing' ||
          !record.data.show_start_mqtt;
        button.style.display = shouldBeVisible ? '' : 'none';
      }
    };

    onMounted(() => {
      if (this.model.config.resModel === 'mrp.production') {
        updateButtonsVisibility();
      }
    });

    useEffect(
      () => {
        if (this.model.config.resModel === 'mrp.production') {
          updateButtonsVisibility();
        }
      },
      () => {
        const record = this.model.root;
        return record?.data ? [record.data.show_start_mqtt] : [];
      }
    );
  },
});
