<template>
    <div class="cart_item">
        <div class="cart_column column_1">
            <el-checkbox class="my_el_checkbox" v-model="course.selected"></el-checkbox>
        </div>
        <div class="cart_column column_2">
            <img src="/static/image/python.jpg" alt="">
            <span><router-link :to="'/course/detail/'+course.id">{{course.name}}</router-link></span>
        </div>
        <div class="cart_column column_3">
            <el-select v-model="expire" size="mini" placeholder="请选择购买有效期" class="my_el_select">
                <el-option label="1个月有效" value="30" key="30"></el-option>
                <el-option label="2个月有效" value="60" key="60"></el-option>
                <el-option label="3个月有效" value="90" key="90"></el-option>
                <el-option label="永久有效" value="10000" key="10000"></el-option>
            </el-select>
        </div>
        <div class="cart_column column_4">¥{{course.price.toFixed(2)}}</div>
        <div class="cart_column column_4" @click="">删除</div>
    </div>
</template>

<script>
    export default {
        name: "CartItem",
        data() {
            return {
                expire: '有效期',
            }
        },
        //接收父组件传递过来的参数
        props: ['course'],
        watch: {
            //通过检测selected的变化切换选中状态
            'course.selected': function () {
                //当勾选状态改变时，向后端发送请求
                this.check_select()
            }
        },
        methods: {
            //状态切换
            check_select() {
                let token = sessionStorage.token

                this.$axios.patch('http://127.0.0.1:9001/cart/option/', {
                    selected: this.course.selected,
                    course_id: this.course.id,
                }, {
                    headers: {
                        //提交token必须在请求头声明token,jwt后必须有空格(通过空格截取jwt和token)
                        'Authorization': 'jwt ' + token,
                    }
                }).then(res => {
                    this.$message.success(res.data.message)
                }).catch(error => {
                    this.$message.error(error.response)
                })
            }
        }
    }
</script>

<style scoped>
    .cart_item::after {
        content: "";
        display: block;
        clear: both;
    }

    .cart_column {
        float: left;
        height: 250px;
    }

    .cart_item .column_1 {
        width: 88px;
        position: relative;
    }

    .my_el_checkbox {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        top: 0;
        margin: auto;
        width: 16px;
        height: 16px;
    }

    .cart_item .column_2 {
        padding: 67px 10px;
        width: 520px;
        height: 116px;
    }

    .cart_item .column_2 img {
        width: 175px;
        height: 115px;
        margin-right: 35px;
        vertical-align: middle;
    }

    .cart_item .column_3 {
        width: 197px;
        position: relative;
        padding-left: 10px;
    }

    .my_el_select {
        width: 130px;
        height: 28px;
        position: absolute;
        top: 0;
        bottom: 0;
        margin: auto;
    }

    .cart_item .column_4 {
        padding: 67px 10px;
        height: 116px;
        width: 142px;
        line-height: 116px;
    }

</style>

