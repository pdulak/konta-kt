function fill_transaction_row(e, rowToFill) {
    // date
    dateCell = document.createElement("td");
    $(dateCell).html(e.date);
    rowToFill.appendChild(dateCell);

    // transaction
    transactionCell = document.createElement("td");
    if (e.irrelevant) {
        transactionCell.style.color = '#aaa';
    }
    transactionCell.innerHTML = e.description + '<div class="text-right">category: ' + e.category__name + '</div>' +
            '<div class="text-right">account: ' + e.account__bank__name + ' - ' + e.account__name + '; type: ' + e.type + '</div>';
    rowToFill.appendChild(transactionCell);

    // amount
    amountCell = document.createElement("td");
    amountCell.setAttribute('class','text-right');
    amountCell.innerHTML = e.amount_account_currency + ' ' + e.account__currency__name;
    rowToFill.appendChild(amountCell);

    return rowToFill;
}

function fill_transactions(data) {
    var bodyToFill = $('#transactions_table tbody');
    var lastDate;
    var t = data.transactions_list;

    document.filters.startDate.value = data.startDate;
    document.filters.endDate.value = data.endDate;

    bodyToFill.empty();

    t.forEach(function(e){
        thisRow = document.createElement("tr");
        thisRow.setAttribute('data-transaction-id', e.id);
        if (lastDate != e.date) {
            thisRow.style.borderTop = "4px solid black";
            lastDate = e.date;
        }

        thisRow = fill_transaction_row(e, thisRow);


        bodyToFill.append(thisRow);
    });
}

function load_transactions() {
    $('#transactions_table').addClass('loading');

    $.ajax({
        type: "POST",
        url: /j_transactions/,
        data: $(document.filters).serialize(),
        success: function(data) {
            if (data.transactions_list) {
                fill_transactions(data);
            } else {
                alert('transactions not loaded');
            }
            $('#transactions_table').removeClass('loading');
        },
        dataType: 'json',
        failure: function(errMsg) {
            $('#transactions_table').removeClass('loading');
            alert(errMsg);
        }
    });
}

function reset_filters() {
    document.filters.irrelevant.selectedIndex = 0;
    document.filters.direction.selectedIndex = 0;
    if (document.filters.account.tagName == "SELECT") {
        document.filters.account.selectedIndex = 0;
    }
    document.filters.startDate.value = "";
    document.filters.endDate.value = "";
    load_transactions();
}

Date.prototype.yyyymmdd = function() {
    var yyyy = this.getFullYear();
    var mm = this.getMonth() < 9 ? "0" + (this.getMonth() + 1) : (this.getMonth() + 1); // getMonth() is zero-based
    var dd  = this.getDate() < 10 ? "0" + this.getDate() : this.getDate();
    return "".concat(yyyy).concat("-").concat(mm).concat("-").concat(dd);
};

$(function(){
    load_transactions();
    $('.monthlyReview li span').on('click',function(e){
        // calculate
        dateArr = $(this).data('date').split('-');
        firstDay = new Date(dateArr[0], dateArr[1]-1, 1);
        lastDay = new Date(dateArr[0], dateArr[1], 0);
        // fill
        document.filters.startDate.value = firstDay.yyyymmdd();
        document.filters.endDate.value = lastDay.yyyymmdd();
        // execute reload
        load_transactions();
    })
});