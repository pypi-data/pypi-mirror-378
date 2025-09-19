import {AbstractSDC, app} from 'sdc_client';

export class SdcListViewController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/sdc_tools/sdc_list_view"; //<sdc-list-view></sdc-list-view>
        this.search_values = {};
        this.model_name = null;
        this.template_context = null;

        /**
         * Events is an array of dom events.
         * The pattern is {'event': {'dom_selector': handler}}
         * Uncommend the following line to add events;
         */
        // this.events.unshift({'click': {'.header-sample': (ev, $elem)=> $elem.css('border', '2px solid black')}}});
    }

    //-------------------------------------------------//
    // Lifecycle handler                               //
    // - onInit (tag parameter)                        //
    // - onLoad (DOM not set)                          //
    // - willShow  (DOM set)                           //
    // - onRefresh  (recalled on reload)              //
    //-------------------------------------------------//
    // - onRemove                                      //
    //-------------------------------------------------//

    onInit(model, filter, onUpdate) {
        if (!this.model) {
            if (this.model_name) {
                model = this.model_name;
            }

            this.model = this.newModel(model);
        }
        if (onUpdate) {
            this.on_update = onUpdate;
        }
        if (typeof filter === 'function') {
            filter = filter();
        }
        if (typeof filter === 'object') {
            this.model.filter(filter);
        }

        if (this.on_update) {
            this.model.load().then(() => {
                this.on_update(this.model.values_list);
            });
        }
    }

    onLoad($html) {
        let lc = $html.filter('.list-container');
        if (lc.length === 0) {
            lc = $html.find('.list-container');
        }
        lc.append(this.model.listView(this.search_values, null, null, this.template_context));
        this.model.on_update = this.model.on_create = () => {
            if (this.on_update) {
                this.model.load().then(() => {
                    this.on_update(this.model.values_list);
                });
            }
            this._updateView();
        };
        return super.onLoad($html);
    }

    willShow() {
        return super.willShow();
    }

    onRefresh() {
        this.find('[data-bs-toggle="tooltip"]').each(function() {
            new Tooltip(this);
        });
        return super.onRefresh();
    }

    removeInstance($btn) {
        this.model.delete($btn.data('instance-pk'));
    }

    onSearch(form) {
        const formData = new FormData(form);
        formData.forEach((value, key) => this.search_values[key] = value);
        this._updateView();
    }

    _updateView() {
        const $div = this.model.listView(this.search_values, () => {
            const elems = $('.tooltip.fade.show');
            elems.remove();
            app.reconcile(this, $div, this.find('.list-container .container-fluid').first());
        }, null, this.template_context);
    }
}

app.register(SdcListViewController);