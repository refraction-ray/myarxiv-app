const path = require('path');
const root = path.resolve(__dirname, '..', 'app');
const VueLoaderPlugin = require('vue-loader/lib/plugin');

module.exports = {
    entry: path.join(root, 'frontend/js/index.js'),
    output: {
        path: path.join(root, 'static/build/'),
        filename: 'main-[hash].js',
        publicPath: '/static/build'
    },
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js' // 'vue/dist/vue.common.js'
        }
    },
    module: {
        rules: [{
            test: /.vue$/,
            loader: 'vue-loader'
        },
            {
                test: /\.js$/,
                loader: 'babel-loader'
            },
            {
                test: /cons\.js$/,
                use: ['script-loader']
            },
            {
                test: /\.css$/,
                use: [
                    {loader: "style-loader"},
                    {loader: "css-loader"}
                ]
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin()
    ]
};