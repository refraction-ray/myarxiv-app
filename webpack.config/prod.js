const path = require('path');
const Merge = require('webpack-merge');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const root = path.resolve(__dirname, '..', 'app');
const CommonConfig = require('./base.js');
const CleanWebpackPlugin = require('clean-webpack-plugin');


module.exports = Merge(CommonConfig, {
    mode: 'production',
    output: {
        path: path.join(root, 'static/build/prod'),
        filename: 'main-[hash].js',
        publicPath: '/static/build/prod'
    },
    optimization: {},
    plugins: [
        new HtmlWebpackPlugin({
            filename: path.join(root, 'templates/extprod.html'),
            template: path.join(root, 'frontend/html/extprod.html')
        }),
        new CleanWebpackPlugin(
            [path.join(root, 'static/build/prod')], {
                root: root
            })
    ]
});