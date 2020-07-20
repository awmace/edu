<template>
    <div class="footer">
        <ul>
            <li v-for="(nav,key) in nav_list" v-show="nav.position==2">{{nav.title}}</li>
        </ul>
    </div>
</template>

<script>
    export default {
        name: "Bot",
        //获取导航栏的数据
        data() {
            return {
                nav_list: [],  //轮播图的数据
                i: '',
            }
        },
        methods: {
            get_list_nav() {
                this.$axios({
                    url: 'http://127.0.0.1:9001/home/nav/',
                    method: "get",
                }).then(res => {
                    // 当前请求的返回值可以通过res接受到
                    this.nav_list = res.data;
                }).catch(error => {
                    console.log(error);
                })
            },
        },
        //页面加载之前将数据获取并赋值给data
        created() {
            this.get_list_nav()
        },
    }
</script>

<style scoped>
    .footer {
        width: 100%;
        height: 128px;
        background: #25292e;
        color: #fff;
    }

    .footer ul {
        margin: 0 auto 16px;
        padding-top: 38px;
        width: 810px;
    }

    .footer ul li {
        float: left;
        width: 112px;
        margin: 0 10px;
        text-align: center;
        font-size: 14px;
        list-style: none;
    }

    .footer ul::after {
        content: "";
        display: block;
        clear: both;
    }

    .footer p {
        text-align: center;
        font-size: 12px;
    }
</style>
