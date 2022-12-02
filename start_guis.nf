#!/usr/bin/env nextflow

params.Cellfinder_env
params.Clearmap_env
params.Napari_env
params.run_dir = new File("").getAbsolutePath()
println params.run_dir

process preparation_cellfinder(){
    output:
    stdout into cellfinder_channel

    """
    conda env list | grep Cellfinder_env | awk -F' ' '{print \$NF}'
    """
}

process preparation_clearmap(){
    output:
    stdout into clearmap_channel

    """
    conda env list | grep Clearmap_env | awk -F' ' '{print \$NF}'
    """
}

process preparation_napari(){
    output:
    stdout into napari_channel

    """
    conda env list | grep Napari_env | awk -F' ' '{print \$NF}'
    """
}

process preparation_all(){
    input:
    val cellfinder_path from cellfinder_channel
    val clearmap_path from clearmap_channel
    val napari_path from napari_channel
    output:
    val done into cellfinder_prep
    val done into clearmap_prep
    val done into napari_prep

    exec:
    params.Cellfinder_env = "$cellfinder_path"
    println params.Cellfinder_env
    params.Clearmap_env = "$clearmap_path"
    println params.Clearmap_env
    params.Napari_env = "$napari_path"
    println params.Napari_env
    done = 1
}

process start_cellfinder(){
    input:
    val done from cellfinder_prep
    """
    source activate ${params.Cellfinder_env}
    #echo "" > ${params.run_dir}/cellfinder_log.log
    #python ${params.run_dir}/Cellfinder/gui.py >> ${params.run_dir}/cellfinder_log.log
    """
}


process start_clearmap(){
    input:
    val done from clearmap_prep
    """
    source activate ${params.Clearmap_env}
    #echo "" > ${params.run_dir}/clearmap_log.log
    #python ${params.run_dir}/ClearMap/gui.py >> ${params.run_dir}/clearmap_log.log
    """
}

process start_napari(){
    input:
    val done from napari_prep
    """
    source activate ${params.Napari_env}
    #echo "" > ${params.run_dir}/napari_log.log
    #napari >> ${params.run_dir}/napari_log.log
    """
}
