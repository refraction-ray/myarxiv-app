const path = require('path');
const Merge = require('webpack-merge');
const CommonConfig = require('./base.js');
const HtmlWebpackPlugin = require('html-webpack-plugin');
// const ScriptExtHtmlWebpackPlugin = require('script-ext-html-webpack-plugin')
const CleanWebpackPlugin = require('clean-webpack-plugin');
const root = path.resolve(__dirname, '..', 'app');

module.exports = Merge(CommonConfig, {
    mode: 'development',
    devtool: 'cheap-module-eval-source-map',
    // devServer: {
    //   contentBase: path.resolve(__dirname, 'dist'),
    //   hot: true,
    //   hotOnly: true
    // },
    output: {
        path: path.join(root, 'static/build/dev'),
        filename: 'main-[hash].js',
        publicPath: '/static/build/dev'
    },
    plugins: [
        // new webpack.HotModuleReplacementPlugin(),
        // new webpack.NamedModulesPlugin(),
        new HtmlWebpackPlugin({
            filename: path.join(root, 'templates/extdev.html'),
            template: path.join(root, 'frontend/html/extdev.html')
        }),
        new CleanWebpackPlugin(
            [path.join(root, 'static/build/dev')], {
                root: root
            })
    ]
});