"use strict";
(self["webpackChunkjupyterlab_firefox_launcher"] = self["webpackChunkjupyterlab_firefox_launcher"] || []).push([["lib_launcher_js"],{

/***/ "./lib/launcher.js":
/*!*************************!*\
  !*** ./lib/launcher.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   launchFirefox: () => (/* binding */ launchFirefox)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__);



/**
 * Create a new Firefox iframe widget for the main area
 */
function createFirefoxWidget(url) {
    const content = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.IFrame({
        // Provide sandbox exceptions for Firefox to function properly
        sandbox: [
            'allow-same-origin',
            'allow-scripts',
            'allow-popups',
            'allow-forms',
            'allow-downloads',
            'allow-modals'
        ]
    });
    content.title.label = 'Firefox Desktop';
    content.title.closable = true;
    content.url = url;
    content.addClass('jp-Firefox-iframe');
    content.id = `firefox-desktop-${Date.now()}`;
    const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.MainAreaWidget({ content });
    widget.addClass('jp-Firefox-widget');
    return widget;
}
/**
 * Launch Firefox in a JupyterLab tab using iframe widget
 */
async function launchFirefox(app) {
    try {
        console.log('🔥 Launching Firefox in JupyterLab tab...');
        // Get the Firefox proxy URL directly
        const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
        const firefoxUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__.URLExt.join(settings.baseUrl, 'proxy', 'firefox-desktop');
        console.log('🔥 Firefox URL:', firefoxUrl);
        // Create the iframe widget
        const widget = createFirefoxWidget(firefoxUrl);
        // Add to the main area as a new tab
        app.shell.add(widget, 'main');
        // Activate the new tab
        app.shell.activateById(widget.id);
        console.log('🔥 Firefox widget created and added to shell');
        return widget;
    }
    catch (error) {
        console.error('🔥 Error launching Firefox:', error);
        const errorMsg = error instanceof Error ? error.message : String(error);
        throw new Error(`Failed to launch Firefox: ${errorMsg}`);
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_launcher_js.c05a45d558a43ca45aa3.js.map