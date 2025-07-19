const path = require('path');

const mode = process.env.NODE_ENV === 'production' ? 'production' : 'development';

module.exports = {
  mode: mode,
  entry: './src/index.ts',
  devtool: mode === 'development' ? 'inline-source-map' : false,
  output: {
    filename: 'index.js',
    path: path.resolve(__dirname, 'static'),
    library: {
      name: 'jupyterlab_firefox_launcher',
      type: 'amd',
      export: 'default'
    },
    globalObject: 'this',
    clean: true
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.jsx']
  },
  externals: {
    '@jupyterlab/launcher': 'amd @jupyterlab/launcher',
    '@jupyterlab/ui-components': 'amd @jupyterlab/ui-components',
    '@jupyterlab/translation': 'amd @jupyterlab/translation',
    '@jupyterlab/apputils': 'amd @jupyterlab/apputils',
    '@jupyterlab/services': 'amd @jupyterlab/services',
    '@jupyterlab/coreutils': 'amd @jupyterlab/coreutils'
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: [
          {
            loader: 'ts-loader',
            options: {
              transpileOnly: true
            }
          }
        ],
        exclude: /node_modules/
      },
      {
        test: /\.css$/i,
        use: ['raw-loader']
      },
      {
        test: /\.svg$/,
        use: ['raw-loader']
      },
      {
        test: /\.(png|jpe?g|gif)$/i,
        use: [
          {
            loader: 'file-loader'
          }
        ]
      }
    ]
  },
  externals: [
    '@jupyterlab/application',
    '@jupyterlab/apputils',
    '@jupyterlab/coreutils',
    '@jupyterlab/launcher',
    '@jupyterlab/services',
    '@jupyterlab/translation',
    '@jupyterlab/ui-components',
    '@lumino/widgets',
    'react'
  ]
};
