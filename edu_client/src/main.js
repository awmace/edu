// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store/index'

// axios配置
import axios from "axios";

Vue.prototype.$axios = axios;

//element-ui
import Element from "element-ui"
import 'element-ui/lib/theme-chalk/index.css'

// 导入极验
import "../static/js/gt"

// 全局css
import "../static/css/global.css"

Vue.use(Element);

// vue-video-player
require('video.js/dist/video-js.css');
require('vue-video-player/src/custom-theme.css');
import VideoPlayer from 'vue-video-player'

Vue.use(VideoPlayer);

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    //注册虚拟机
    store,
    components: {App},
    template: '<App/>'
})
