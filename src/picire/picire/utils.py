def generate_log(config_idx, prefix="", print_idx=False, threshold=None):
    config_idx.sort()
    info_to_print = "\t%s " % prefix
    info_to_print += "%d elements. " % len(config_idx)

    if print_idx:
        if threshold != None:
            if len(config_idx) > threshold:
                info_to_print += "Idx: %r ... %r" % (config_idx[:5], config_idx[-5:])
            else:
                info_to_print += "Idx: %r" % config_idx

    return info_to_print
