/*
https://github.com/InventPartners/bootstrap-responsive-tabs

Copyright Invent Partners
http://www.inventpartners.com

The following license applies to all parts of this software except as
documented below:

====

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

==== 
*/

(function( $ ) {
    function storeTabs($tabs, $destination) {
        // measure width
        $tabs.each(function() {
            var width = $(this).outerWidth(true);
            $(this).find('a').data('width', width);
        });
        $tabs.prependTo($destination);

        $tabs.find('a').unwrap().removeClass('nav-link').addClass('dropdown-item');
    }
    function makeTabsResponsive($element) {

        var $tabs = $element.find('li');
        var $firstTab = $tabs.first();

        var individualTabHeight = $firstTab.outerHeight();
        var tabsHeight = $element.outerHeight();

        if(tabsHeight > individualTabHeight) {
            // get y pos of first tab
            var firstTabPos = $firstTab.offset();

            var thisTabPos;
            $tabs.each(function() {

                var $thisTab = $(this);

                thisTabPos = $thisTab.offset();

                if(thisTabPos.top > firstTabPos.top) {

                    var $dropdown = $element.find('.responsivetabs-more');
                            
                    if(!$dropdown.length) {
                        var dropdownMarkup = '<li class="dropdown show responsivetabs-more" style="margin-bottom: -10px;">'
                        + '<a href="#" class="dropdown-toggle" data-toggle="dropdown" style="font-size: 35px; padding: 10px"></a>'
                        + '<div class="dropdown-menu ft-dropdown-menu-dark dropdown-menu-right">'
                        + '</div></li>';
                        $dropdown = $(dropdownMarkup);
                        $element.append($dropdown);
                    }

                    var $previousTab = $thisTab.prev();
                    var $followingTabs = $thisTab.nextAll().not('.dropdown');

                    var $destination = $('.dropdown-menu', $dropdown);

                    if(!$thisTab.hasClass('dropdown')) {
                        storeTabs($followingTabs, $destination);
                        storeTabs($thisTab, $destination);
                    }
                    storeTabs($previousTab, $destination);

                    return;

                }

            });

        } else {
            // check if enough space to move a menu item back out of "..."
            // get parent width
            var parentWidth = $element.parent().width();
            var tabSetWidth = 0;
            var xPxAvailable;

            // calculate total width of tab set (can't just use width of ul because it is 100% by default)
            $element.children('li').each(function() {
                tabSetWidth += $(this).outerWidth(true);
            });

            // calculate available horizontal space
            xPxAvailable = parentWidth - tabSetWidth;

            $element.find('.dropdown-menu a').each(function() {
                if($(this).data('width') <= xPxAvailable) {

                    // fix for bootstrap 4
                    $(this).removeClass('dropdown-item').addClass('nav-link');

                    $(this).insertBefore($element.find('.responsivetabs-more')).wrap('<li class="nav-item"></li>'); 
                    xPxAvailable -= $(this).data('width');
                } else {
                    return false;
                } 
            });

            // if no menu items left, remove "..."
            if(!$element.find('.dropdown-menu a').length) {
                $element.find('.responsivetabs-more').remove();
            }
        }

    }

    $.fn.responsiveTabs = function() {

        this.each(function() {
            var tabs = $(this);
            makeTabsResponsive(tabs); 
            $(window).resize(function() {
                makeTabsResponsive(tabs); 
            });
        });
        return this;
    };
})( jQuery );
