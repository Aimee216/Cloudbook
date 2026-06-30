function fmtStatus(v) {
    const m = {"正常":"badge-green","离职":"badge-gray","上架":"badge-green","下架":"badge-red","待支付":"badge-green","待发货":"badge-gray","已发货":"badge-green","已完成":"badge-blue","已取消":"badge-red","库存偏高":"badge-orange"};
    return v;
}
