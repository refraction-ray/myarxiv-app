import Vue from 'vue'
import paginate from './paginate.vue'
import navBar from './navBar.vue'
import refreshBoard from './refreshBoard.vue'
import flash from './flash.vue'
import cons from './cons.js'
import {datewithspace} from './filters.js'
import VCalendar from 'v-calendar';
import 'v-calendar/lib/v-calendar.min.css';
import '../css/style.css'
import './cons.js'

window.Vue = Vue;

Vue.use(VCalendar, {
  firstDayOfWeek: 2  // Monday
});

Vue.component('paginate', paginate);
Vue.component('navBar', navBar);
Vue.component('refreshBoard', refreshBoard);
Vue.component('flash', flash);

Vue.filter("datewithspace", function(v) {return datewithspace(v)});
