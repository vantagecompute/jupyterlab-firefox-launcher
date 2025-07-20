"use strict";
(self["webpackChunkjupyterlab_firefox_launcher"] = self["webpackChunkjupyterlab_firefox_launcher"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   firefoxIcon: () => (/* binding */ firefoxIcon)
/* harmony export */ });
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");
/* harmony import */ var _style_icons_firefox_icon_svg__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../style/icons/firefox-icon.svg */ "./style/icons/firefox-icon.svg");



// Import styles  

// Import Firefox SVG icon

// Create the Firefox icon
const firefoxIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.LabIcon({
    name: 'firefox-launcher:firefox',
    svgstr: _style_icons_firefox_icon_svg__WEBPACK_IMPORTED_MODULE_4__
});
console.log('🔥 Firefox icon created:', firefoxIcon);
console.log('🔥 Firefox SVG content length:', _style_icons_firefox_icon_svg__WEBPACK_IMPORTED_MODULE_4__?.length || 'undefined');
/**
 * Initialization data for the firefox-launcher extension.
 */
const plugin = {
    id: 'jupyterlab-firefox-launcher:plugin',
    description: 'A JupyterLab extension to launch Firefox in a tab',
    autoStart: true,
    requires: [_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__.ILauncher],
    optional: [_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__.ITranslator],
    activate: (app, launcher, translator) => {
        const trans = (translator ?? _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_2__.nullTranslator).load('jupyterlab');
        console.log('🔥 JupyterLab extension jupyterlab-firefox-launcher is activated!');
        console.log('🔥 Launcher available:', !!launcher);
        console.log('🔥 App commands:', app.commands);
        // Register the launch command first
        app.commands.addCommand('firefox-launcher:launch', {
            label: 'Firefox',
            caption: 'Launch Firefox in a new tab',
            icon: firefoxIcon,
            execute: async () => {
                console.log('🔥 Firefox launcher command executed!');
                try {
                    // Lazy load the launcher module and return the widget
                    const { launchFirefox } = await __webpack_require__.e(/*! import() */ "lib_launcher_js").then(__webpack_require__.bind(__webpack_require__, /*! ./launcher */ "./lib/launcher.js"));
                    return launchFirefox(app);
                }
                catch (error) {
                    console.error('🔥 Error launching Firefox:', error);
                    throw error;
                }
            }
        });
        console.log('🔥 Firefox command registered');
        // Add Firefox launcher to the "Other" category
        if (launcher) {
            const translatedCategory = trans.__('Other');
            const hardcodedCategory = 'Other';
            console.log('🔥 Translated category:', JSON.stringify(translatedCategory));
            console.log('🔥 Hardcoded category:', JSON.stringify(hardcodedCategory));
            console.log('🔥 Are they equal?', translatedCategory === hardcodedCategory);
            // Use translated version to match Terminal and FileEditor patterns
            launcher.add({
                command: 'firefox-launcher:launch',
                category: trans.__('Other'),
                rank: 0
            });
            console.log('🔥 Firefox launcher added with translated category');
        }
        else {
            console.error('🔥 Launcher not available - cannot add Firefox launcher');
        }
    }
};
// Export the plugin as the default export
const extension = plugin;
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extension);


/***/ }),

/***/ "./style/icons/firefox-icon.svg":
/*!**************************************!*\
  !*** ./style/icons/firefox-icon.svg ***!
  \**************************************/
/***/ ((module) => {

module.exports = "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\">\n<path d=\"M21.85 11.1a8.96 8.96 0 0 0-1.9-3.7 11.2 11.2 0 0 0-.6-.8c-.3-.3-.5-.7-.8-1a9.3 9.3 0 0 0-6.5-2.6c-1.4 0-2.7.3-3.9.9a9.3 9.3 0 0 0-5.8 8.6c0 5.1 4.2 9.3 9.3 9.3 3.8 0 7-2.3 8.4-5.6.7-1.6 1-3.4.8-5.1zM12 21.3c-4.6 0-8.3-3.7-8.3-8.3 0-4.6 3.7-8.3 8.3-8.3 4.6 0 8.3 3.7 8.3 8.3 0 4.6-3.7 8.3-8.3 8.3z\" fill=\"#FF7139\"/>\n<path d=\"M18.5 8.8c-.4-.8-1-1.5-1.7-2.1-.7-.6-1.5-1-2.4-1.3a8.8 8.8 0 0 0-2.4-.3c-1.7 0-3.3.6-4.5 1.7a6.5 6.5 0 0 0-1.9 4.6c0 .9.2 1.8.6 2.6.4.8 1 1.5 1.7 2.1.7.6 1.5 1 2.4 1.3.8.3 1.6.4 2.4.3 1.7 0 3.3-.6 4.5-1.7a6.5 6.5 0 0 0 1.9-4.6c0-.9-.2-1.8-.6-2.6z\" fill=\"#FF5722\"/>\n<path d=\"M15.8 10.4c-.2-.4-.5-.7-.8-1-.3-.3-.7-.5-1.1-.6-.4-.1-.8-.2-1.2-.1-.6.1-1.1.4-1.5.8-.4.4-.7.9-.8 1.5-.1.6 0 1.2.3 1.7.3.5.7.9 1.2 1.1.5.2 1 .3 1.5.2.6-.1 1.1-.4 1.5-.8.4-.4.7-.9.8-1.5.1-.4 0-.8-.1-1.2z\" fill=\"#FFFFFF\"/>\n</svg>";

/***/ })

}]);
//# sourceMappingURL=lib_index_js.24fe269622f3b7027b3b.js.map