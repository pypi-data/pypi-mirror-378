import {AbstractSDC, app} from 'sdc_client';


export class SdcDetailViewController extends AbstractSDC {

    constructor() {
        super();
        this.contentUrl = "/sdc_view/sdc_tools/sdc_detail_view"; //<sdc-detail-view></sdc-detail-view>
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

    onInit(model, pk) {
        if (!model || typeof pk === 'undefined') {
            console.error("You have to set data-model and data-pk in the <sdc-detail-view> tag!");
        }
        this.model = this.newModel(model, {pk: pk});
    }

    onLoad($html) {
        const $elem = $html.filter('.detail-container').append(this.model.detailView(null, null, null, this.template_context));
        this.model.on_update = this.model.on_create = () => {
            $elem.empty().append(this.model.detailView( null, null, null, this.template_context));
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


    removeInstance($btn, e) {
        this.model.delete();
    }

}

app.register(SdcDetailViewController);