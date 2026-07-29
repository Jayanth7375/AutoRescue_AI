package com.example.network

import android.util.Log
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit

object NetworkConfig {

    private const val DEBUG_BASE_URL = "http://127.0.0.1:8000/"
    const val BASE_URL = DEBUG_BASE_URL

    init {
        Log.d("AutoRescueDebug", "NetworkConfig initialized - BASE_URL=$BASE_URL")
    }

    val baseUrl: String
        get() = DEBUG_BASE_URL

    private val moshi: Moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val loggingInterceptor: HttpLoggingInterceptor
        get() = HttpLoggingInterceptor { message ->
            Log.d("OkHttp", message)
        }.apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

    private val okHttpClient: OkHttpClient
        get() = OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .callTimeout(130, TimeUnit.SECONDS)
            .addInterceptor(loggingInterceptor)
            .build()

    val retrofit: Retrofit
        get() = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create(moshi))
            .build()

    val autoRescueApi: AutoRescueApi
        get() = retrofit.create(AutoRescueApi::class.java)
}
