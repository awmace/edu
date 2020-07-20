<template>
    <div class="cart_item">
        <div class="cart_column column_1">
            <el-checkbox class="my_el_checkbox" v-model="course.selected"></el-checkbox>
        </div>
        <div class="cart_column column_2">
            <img :src="course.course_img" alt="">
            <span><router-link :to="'/course/detail/'+course.id">{{course.name}}</router-link></span>
        </div>
        <div class="cart_column column_3">
            <el-select v-model="course.expire_id" size="mini" placeholder="请选择购买有效期" class="my_el_select">
                <el-option
                    :label="item.expire_text" :value="item.id" :key="item.id" v-for="item in course.expire_list">
                </el-option>
            </el-select>
        </div>
        <div class="cart_column column_4">¥{{course.real_price}}</div>
        <div class="cart_column column_4" @click="delete_course(course.id)">删除</div>
    </div>
</template>

<script>
    export default {
        name: "CartItem",
        data() {
            return {
                expire: '1个月有效',
            }
        },
        //接收父组件传递过来的参数
        props: ['course'],
        watch: {
            //通过检测selected的变化切换选中状态
            'course.selected': function () {
                //当勾选状态改变时，向后端发送请求
                this.check_select()
            },
            // 切换课程有效期
            'course.expire_id': function () {
                // 后台发送请求切换状态
                this.change_expire()
            }
        },
        methods: {
            //删除购物车商品
            delete_course(course_id) {
                console.log(course_id)
                let token = sessionStorage.token

                this.$axios.delete('http://127.0.0.1:9001/cart/rmcart/'+course_id+'/', {
                    headers: {
                        //提交token必须在请求头声明token,jwt后必须有空格(通过空格截取jwt和token)
                        'Authorization': 'jwt ' + token,
                    }
                }).then(res => {
                    this.$message.success(res.data.message)

                    this.$emit('delete_course')

                }).catch(error => {
                    this.$message.error(error.response)
                })
            },
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

                    this.$emit('change_select')

                }).catch(error => {
                    this.$message.error(error.response)
                })
            },

            //有效期切换
            change_expire() {
                let token = sessionStorage.token;

                this.$axios.put('http://127.0.0.1:9001/cart/option/', {
                    expire_id: this.course.expire_id,
                    course_id: this.course.id
                }, {
                    headers: {
                        "Authorization": "jwt " + token,
                    }
                }).then(response => {
                    console.log(response.data);

                    // 更新切换有效期后课程的价格
                    this.course.real_price = response.data.real_price;

                    this.$message.success("切换有效期成功");
                    this.$emit('change_select')
                }).catch(error => {
                    console.log(error);
                })
            },
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

