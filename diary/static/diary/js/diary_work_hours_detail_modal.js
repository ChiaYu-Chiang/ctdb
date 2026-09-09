// Populates #workHoursDetailModal with the clicked work-hours item's full
// detail. Uses jQuery (already loaded by base.html for Bootstrap 4) because
// Bootstrap's modal show/hide events are jQuery custom events, and jQuery's
// own `.on()` is the most reliable way to catch them across Bootstrap 4
// versions/browsers.
$(function () {
    $('#workHoursDetailModal').on('show.bs.modal', function (event) {
        const trigger = event.relatedTarget;
        if (!trigger) {
            return;
        }
        const data = trigger.dataset;
        const modal = $(this);
        modal.find('#workHoursDetailOrderNumber').text(data.orderNumber || '');
        modal.find('#workHoursDetailCustomerName').text(data.customerName || '');
        modal.find('#workHoursDetailSalesRep').text(data.salesRep || '');
        modal.find('#workHoursDetailProductCategory').text(data.productCategory || '');
        modal.find('#workHoursDetailRequirement').text(data.requirement || '');
        modal.find('#workHoursDetailHandlingContent').text(data.handlingContent || '');
        modal.find('#workHoursDetailHours').text(data.hours ? data.hours + 'hr' : '');
    });
});