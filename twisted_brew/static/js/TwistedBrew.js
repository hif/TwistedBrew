var tb = angular.module("TwistedBrew", ["ngCookies"]); //, "TwistedBrewControllers"]);
tb.config([
    '$httpProvider',
    '$interpolateProvider',
    '$resourceProvider',
    function($httpProvider, $interpolateProvider, $resourceProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $resourceProvider.defaults.stripTrailingSlashes = false;
    }]).
    run([
    '$http',
    '$cookies',
    function($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    }]);
])